#include "se/world.hpp"
#include "se/activity_wave.hpp"
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
using namespace se;
int main(int argc,char**argv){if(argc!=2)throw std::runtime_error("fixture path");std::ifstream in(argv[1]);if(!in)throw std::runtime_error("fixture missing");std::string line,tag;int W,H,R,bx,by,n,x1,y1,x2,y2;char o;while(std::getline(in,line)){if(line.starts_with("WORLD")){std::istringstream s(line);s>>tag>>W>>H>>R>>bx>>by>>o>>n>>x1>>y1>>x2>>y2;break;}}World world(W,H,R);world.initialize({bx,by,o},{{x1,y1},{x2,y2}});std::getline(in,line);std::istringstream fs(line);int tick,count,ex1,ey1,ex2,ey2;fs>>tag>>tick>>count>>ex1>>ey1>>ex2>>ey2;auto f=world.perceive(tick);std::vector<std::pair<int,int>> occupied;for(auto&c:f.cells)if(c.occupied)occupied.push_back({c.dx,c.dy});std::sort(occupied.begin(),occupied.end());if(occupied!=std::vector<std::pair<int,int>>{{ex1,ey1},{ex2,ey2}})return 1;std::getline(in,line);std::istringstream as(line);int action,wbx,wby,ox1,oy1,ox2,oy2;std::string outcome;as>>tag>>action>>outcome>>wbx>>wby>>ox1>>oy1>>ox2>>oy2;auto result=world.apply((ActionType)action);if(result!=ActionResult::Success||world.body().x!=wbx||world.body().y!=wby||world.objects()[0].x!=ox1||world.objects()[0].y!=oy1||world.objects()[1].x!=ox2||world.objects()[1].y!=oy2)return 2;std::getline(in,line);std::istringstream ps(line);int source,target;float expected;ps>>tag>>source>>action>>target>>expected;CognitiveGraph g;g.add_cognit(1);g.add_cognit();auto&e=g.connect(source,target,RelationType::SelfAction,(std::uint8_t)action);e.strength=e.prediction=1;e.confidence=.75f;std::uint32_t active[]={(std::uint32_t)source};auto p=g.predict(active,(ActionType)action);if(std::abs(p[target]-expected)>1e-6||g.predict(active,ActionType::MoveDown).contains(target))return 3;auto wave=propagate(g,active,1);if(wave.active.size()!=2)return 4;

RelationStore rs;rs.resize_nodes(2);auto[e1,h1]=rs.connect(0,1,RelationType::Associative);if(e1.status!=RelationStatus::Provisional)return 5;rs.consolidate(h1);if(e1.status!=RelationStatus::Consolidated)return 6;auto st=rs.state(0,h1);st.status=(std::uint8_t)RelationStatus::Provisional;rs.update(h1,st);if(rs.get(h1)->status!=RelationStatus::Provisional)return 7;

World multi_world(20,20,4);Body b1{5,5,'N',0,1,10};Body b2{8,8,'N',0,2,20};multi_world.initialize_multi({b1,b2},{{1,5,4,0}});auto mf=multi_world.perceive(1,10);if(mf.cells.empty()||multi_world.resistance(10)!=0.0)return 8;auto res=multi_world.apply(ActionType::MoveUp,10);if(res!=ActionResult::Success)return 9;std::uint32_t b_ids[]={10,20};std::uint8_t b_acts[]={(std::uint8_t)ActionType::MoveDown,(std::uint8_t)ActionType::MoveDown};auto intent_results=multi_world.resolve_intents(b_ids,b_acts);if(intent_results.size()!=2)return 10;

std::cout<<"python fixture equivalence passed\n";}
