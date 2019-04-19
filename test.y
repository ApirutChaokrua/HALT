%{
void yyerror (char *s);
static int yylex();
#include <stdio.h>     /* C declarations used in actions */
#include <stdlib.h>
#include <ctype.h>
int symbols[52];
int symbolVal(char symbol);
void updateSymbolVal(char symbol, int val);
%}

%union {int num; char id;}         /* Yacc definitions */
%start line
%token SHOW 
%token ASSIGN_OP 
%token DEF VAR IF SHOWLN LOOP RETURN BREAK LE_OP GE_OP EQ_OP MOD_OP 
%token L_BRACKET R_BRACKET L_CBRACKET R_CBRACKET L_ABRACKET R_ABRACKET
%token exit_command tok_EOF
%token EOL    "end-of-line"
%token <num> number
%token <id> identifier
%type <num> line exp term exp2 
%type <id> assignment
%locations

%right "<-" 
%left LE_OP GE_OP EQ_OP 
%left '+' '-'  
%left '*' '/' 

%%

/* descriptions of expected inputs     corresponding actions (in C) */


line    : assignment EOL	{;}
		| exit_command 		{exit(EXIT_SUCCESS);}
		| SHOW exp 		EOL	{printf("Printing %d\n", $2);}
		| line assignment EOL	{;}
		| line SHOW exp EOL	{printf("Printing %d\n", $3);}
		| line exit_command	{exit(EXIT_SUCCESS);}
		| error { yyerror(" line error\n"); }
        ;


assignment : identifier ASSIGN_OP exp  { updateSymbolVal($1,$3); }
			;
exp    	: exp2	{;}
		| exp '+' exp2          {$$ = $1 + $3;}
		| exp '-' exp2          {$$ = $1 - $3;}
       	;
exp2		:	 term                  {$$ = $1;}
		| exp2 '*' term          {$$ = $1 * $3;}
		| exp2 '/' term          { 
                                    if ($3 == 0){
                                        yyerror ("invalid division by zero");
                                        YYERROR;
                                    }
                                    else
                                        $$ = $1 / $3;
								 }
				;
term   	: number                {$$ = $1;}
		| identifier			{$$ = symbolVal($1);} 
        ;

%%                     /* C code */

int computeSymbolIndex(char token)
{
	int idx = -1;
	if(islower(token)) {
		idx = token - 'a' + 26;
	} else if(isupper(token)) {
		idx = token - 'A';
	}
	return idx;
} 

/* returns the value of a given symbol */
int symbolVal(char symbol)
{
	int bucket = computeSymbolIndex(symbol);
	return symbols[bucket];
}

/* updates the value of a given symbol */
void updateSymbolVal(char symbol, int val)
{
	int bucket = computeSymbolIndex(symbol);
	symbols[bucket] = val;
}


#include"lex.yy.c"  


int main(int argc, char **argv){
	int input=1;
    	yyin = fopen(argv[1], "r");

	return yyparse ( );
}

void yyerror (char *s) {
	fprintf (stderr, "Line : %d, %s\n",yylineno, s);
} 