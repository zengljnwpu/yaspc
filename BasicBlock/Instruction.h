//#pragma once
#ifndef _INSTRUCTION_H_
#  define _INSTRUCTION_H_

#include <iostream>
using namespace std;
enum { Branch, Assign, Others };

class Instruction
{
private:
	int type;
	string context;
	int lineNum;
	bool labeled;
	string label;
	string gotoLabel;
	//op
public:
	Instruction()
	{
		type = Others;
	}
	Instruction(string context)
	{
		setInst(context);
	}
	void setInst(string context)
	{
		this->context = context;
		int tmp_pos = context.find("goto");
		if (tmp_pos == std::string::npos)
		{
			this->type = Assign;
		}
		else
		{
			this->type = Branch;
			string tmpstr = context.substr(tmp_pos + 4, context.length());
			tmpstr.erase(0, tmpstr.find_first_not_of(" "));
			tmpstr.erase(tmpstr.find_last_not_of(" ")+1);
			this->gotoLabel = tmpstr;
		}

		//label和goto可能同时存在
		int position = context.find(":");
		if (position == std::string::npos)
		{
			this->labeled = false;
		}
		else
		{
			string temp = context.substr(0, position);
			temp.erase(0, temp.find_first_not_of(" "));
			temp.erase(temp.find_last_not_of(" ") + 1);
			this->label = temp;
			this->labeled = true;
		}


	}
	int getType()
	{
		return type;
	}
	void setLineNum(int LineNum)
	{
		this->lineNum = LineNum;
	}
	bool isLabeled()
	{
		return this->labeled;
	}
	string getLabel()
	{
		return this->label;
	}
	string getgotoLabel()
	{
		return this->gotoLabel;
	}

};

#endif // _INSTRUCTION_H_
