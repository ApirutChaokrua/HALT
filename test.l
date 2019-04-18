D			[0-9]
L			[a-zA-Z_]
H			[a-fA-F0-9]
E			[Ee][+-]?{D}+
FS		(f|F|l|L)
IS		(u|U|l|L)*

%{
#include "test.tab.h"
void yyerror (char *s);
int yylex();
%}

%option yylineno

%%
"exit"				  { return exit_command;}
"#DEF"		    	{ return DEF; }
"#VAR"		    	{ return VAR; }
"#IF"			      { return IF; }
"SHOW"				  { return SHOW;}
"SHOWLN"	    	{ return SHOWLN; }
"LOOP"		    	{ return LOOP; }
"RETRUN"        { return RETURN;}
"STOP"          { return BREAK;}    
"<="		    	  { return LE_OP; }
">="		    	  { return GE_OP; }
"=="			      { return EQ_OP; }
"mod"		    	  { return MOD_OP; }
"("			        { return L_BRACKET; }   // round brackets
")"			        { return R_BRACKET; }
"{"			        { return L_CBRACKET; }  // curly brackets
"}"			        { return R_CBRACKET; }
"<"			        { return L_ABRACKET; }  // angle brackets
">"			        { return R_ABRACKET; }
"<-"			      { return ASSIGN_OP; }


{L}({L}|{D})*			   {yylval.id = yytext[0]; return identifier;}
{D}+                  {yylval.num = atoi(yytext); return number;}
[ \t]                ;
[-+=*/;]           	   {return yytext[0];}

.                      {ECHO; yyerror ("unexpected character");}

%%
int yywrap (void) {return 1;}