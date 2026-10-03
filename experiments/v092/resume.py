"""Resume interrupted evaluation without replacing completed measurements."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path

from experiments.scenario_runner import _write_result
from simulation.scenario import artifact_checksum
from .protocol import Curriculum, GROUPS, load_protocol, scenario_path
from .runner import compact, run_trial, trial_id


def validate_saved(protocol, case, seed, group, brain, stage, row):
    expected = dict(protocol_checksum=protocol.checksum, scenario=case['scenario'],
                    scenario_checksum=artifact_checksum(scenario_path(case['scenario'])),
                    brain_checksum=artifact_checksum(brain) if brain else 'FRESH',
                    seed=seed, group=group, stage=stage, horizon=case['horizon'],
                    trial_id=trial_id(stage, case['scenario'], seed, group))
    for key, value in expected.items():
        if row.get(key) != value:
            raise ValueError(f"saved trial mismatch: {expected['trial_id']} / {key}")
    if not row.get('trajectory') or row['trajectory'][-1]['time'] != case['horizon']:
        raise ValueError('saved trial does not reach the declared horizon')


def _job(job):
    canonical, case, seed, group, brain, stage, output = job
    protocol = Curriculum(canonical)
    target = Path(output)/'trials'/(trial_id(stage, case['scenario'], seed, group)+'.json')
    if target.exists():
        raise ValueError('refusing to replace a completed trial')
    _, row = run_trial(protocol, case, seed, group, Path(brain) if brain else None, stage)
    if target.exists():
        raise ValueError('refusing to replace a completed trial')
    _write_result(target, row)
    print('Resumed:', row['trial_id'], flush=True)


def resume(protocol, output, workers=1):
    output = Path(output).resolve()
    lock = json.loads((output/'protocol-lock.json').read_text(encoding='utf-8'))
    data = json.loads((output/'training.json').read_text(encoding='utf-8'))
    if lock['protocol_checksum'] != protocol.checksum or data['protocol_checksum'] != protocol.checksum:
        raise ValueError('protocol checksum mismatch')
    expected_episodes = sum(c['episodes'] for s in protocol.data['STAGES'] for c in s['training'])
    if len(data['episodes']) != expected_episodes:
        raise ValueError('resume requires completed fixed-budget training')
    for checkpoint in data['checkpoints'].values():
        if artifact_checksum(output/checkpoint['path']) != checkpoint['sha256']:
            raise ValueError('checkpoint checksum mismatch')
    specs = []
    for stage in protocol.data['STAGES']:
        brain = output/data['checkpoints'][stage['id']]['path']
        for case in stage['evaluation']:
            for seed in protocol.data['PROTOCOL']['evaluation_seeds']:
                for group in GROUPS:
                    specs.append((case, seed, group, None if group == 'FRESH_FULL' else brain, stage['id']))
    p = protocol.data['PROTOCOL']
    case = dict(scenario=p['counterfactual'], horizon=p['counterfactual_horizon'])
    for group in ('FRESH_FULL', 'EXPERIENCED_FULL'):
        specs.append((case, p['evaluation_seeds'][0], group,
                      None if group == 'FRESH_FULL' else brain, 'counterfactual'))
    jobs = []
    for case, seed, group, brain, stage in specs:
        target = output/'trials'/(trial_id(stage, case['scenario'], seed, group)+'.json')
        if target.exists():
            validate_saved(protocol, case, seed, group, brain, stage,
                           json.loads(target.read_text(encoding='utf-8')))
        else:
            jobs.append((protocol.canonical, case, seed, group, str(brain) if brain else None, stage, str(output)))
    _write_result(output/'resume-log.json', dict(protocol_checksum=protocol.checksum,
                  completed_preserved=len(specs)-len(jobs), missing_trials=len(jobs), workers=workers,
                  training_repeated=False, thresholds_changed=False))
    print(f'Preserving {len(specs)-len(jobs)} completed trials; running {len(jobs)} missing trials', flush=True)
    if workers == 1:
        for job in jobs:
            _job(job)
    else:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            list(executor.map(_job, jobs))
    trials, counter = [], []
    for case, seed, group, brain, stage in specs:
        relative = 'trials/'+trial_id(stage, case['scenario'], seed, group)+'.json'
        row = json.loads((output/relative).read_text(encoding='utf-8'))
        validate_saved(protocol, case, seed, group, brain, stage, row)
        (counter if stage == 'counterfactual' else trials).append(compact(row, relative))
    result = dict(schema='synthetic-life-survival-results', version=1,
                  protocol_checksum=protocol.checksum, software=lock['software'],
                  training=data['episodes'], checkpoints=data['checkpoints'],
                  trials=trials, counterfactual=counter, thresholds_changed_after_full_run=False)
    from .report import analyze, write_report
    result['acceptance'] = analyze(protocol, result, output)
    _write_result(output/'results.json', result)
    write_report(protocol, result, output/'RESULTS.md')
    print('Overall proof:', result['acceptance']['verdict'], flush=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--protocol', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--workers', type=int, choices=(1, 2, 3, 4), default=1)
    args = parser.parse_args()
    resume(load_protocol(args.protocol), args.output, args.workers)
