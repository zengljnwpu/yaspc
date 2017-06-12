#ifndef _BASICBLOCK_H_
#  define _BASICBLOCK_H_

#include <iostream>
#include <cstring>
#include <list>

#include "Instruction.h"
using namespace std;

class BasicBlock
{
	//string& getContext()				//Get the context in which this basic block lives.
	//const Function* getParent()				//Return the enclosing method, or null if none.
	//Instruction* getTerminator();		//Returns the terminator instruction if the block is well formed or null if the block is not well formed.
	//Instruction * 	getFirstNonPHI();		//Returns a pointer to the first instruction in this block that is not a PHINode instruction.
	//iterator 	getFirstInsertionPt();


	//BasicBlock* getSinglePredecessor();
private:
	//BasicBlock* SingleSuccessorBB;
	//BasicBlock* UniqueSuccessorBB;
	int label;
	string gotoLabel;
	list<Instruction*> BlockInst;
	BasicBlock* SingleSuccessorBB;
public:

	void addInst(Instruction *inst)
	{
		BlockInst.push_back(inst);
	}
	void setLabel(int label)
	{
		this->label = label;
	}
	int getLabel()
	{
		return label;
	}
	void setGotoLabel(string gotoLabel)
	{
		this->gotoLabel = gotoLabel;
	}
	string getGotoLabel()
	{
		return this->gotoLabel;
	}
	void setSingleSuccessorBB(BasicBlock* SingleSuccessorBB)
	{
		this->SingleSuccessorBB = SingleSuccessorBB;
	}
	BasicBlock* getSingleSuccessorBB()
	{
		return SingleSuccessorBB;
	}
};

#endif // _BASICBLOCK_H_
