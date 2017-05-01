#include "Instruction.h"
#include "BasicBlock.h"
#include <iostream>
#include <fstream>
#include <list>
#include <map>
#include <cstdlib>
#include <string>

int main()
{
	//读入文件
	ifstream code("input.txt");
	if (!code.is_open())
	{
		cout << "Error opening file" << endl;
		exit(1);
	}

	char buffer[256];
	list<Instruction*> InstList;
	int lineNum = 1;

	//构建指令链表
	while (!code.eof())
	{
		code.getline(buffer, 256);
		Instruction *instr = new Instruction(string(buffer));
		instr->setLineNum(lineNum++);
		InstList.push_back(instr);
	}

	//构建BasicBlock链表
	list<BasicBlock*> BlockList;
	BasicBlock *block = NULL;
	map<string, BasicBlock*> labelmap;
	for (list<Instruction*>::iterator it = InstList.begin(); it != InstList.end(); ++it)
	{
		if (it == InstList.begin() || (*it)->isLabeled())
		{
			if(block != NULL)
				BlockList.push_back(block);
			block = new BasicBlock();
			block->setLabel(BlockList.size()+1);
			//labelmap[(*it)->getLabel] = block;//pair<string, BasicBlock*>
			//labelmap.insert(pair<string, BasicBlock*>((*it)->getLabel, block) );// map<string, int> :: value_type
		}
		if ((*it)->getType() == Branch)
		{
			block->addInst(*it);
			block->setLabel(BlockList.size() + 1);
			block->setGotoLabel((*it)->getgotoLabel());
			labelmap.insert(pair<string, BasicBlock*>((*it)->getLabel(), block));

			BlockList.push_back(block);
			if(it != InstList.end())
			{
				block = new BasicBlock();
				block->setLabel(BlockList.size() + 1);
			}
			

			continue;
		}
		block->addInst(*it);
	}

	for (list<BasicBlock*>::iterator it = BlockList.begin(); it != BlockList.end(); ++it)
	{
		string tmpstr = (*it)->getGotoLabel();
		BasicBlock* tmptarget = labelmap[tmpstr];
		(*it)->setSingleSuccessorBB(tmptarget);
	}


	for (list<BasicBlock*>::iterator it = BlockList.begin(); it != BlockList.end(); ++it)
	{
		int tmpint = (*it)->getLabel();
		cout << tmpint << " ";
		 string tmpstr = (*it)->getGotoLabel();
		cout << tmpstr << endl;
		
	}
	system("pause");
	return 0;
}
