import argparse,json
from .container import inspect_container

def main()->None:
    parser=argparse.ArgumentParser(description="Inspect .sebrain/.seworld metadata without loading a simulation")
    parser.add_argument("path");args=parser.parse_args();print(json.dumps(inspect_container(args.path),indent=2))

if __name__=="__main__":main()
