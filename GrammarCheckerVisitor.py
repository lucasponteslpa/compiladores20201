# Generated from antlr4-python3-runtime-4.7.2/src/autogen/Grammar.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .GrammarParser import GrammarParser
else:
    from GrammarParser import GrammarParser


import sys
err = sys.stderr.write
def printf(string, *args):
    sys.stdout.write(string % args)

import struct
import math
# Função utilizada para transformar um valor float para um valor hexadecimal
# (o equivalente em hexadecimal dos valores dos bits de um float)
def float_to_hex(f):
    float_hex = hex(struct.unpack('<Q', struct.pack('<d', f))[0])
    if (int(float_hex[10],16) % 2 != 0):
        if (float_hex[10] == 'f'):
            float_hex = float(math.ceil(f))
        else:
            float_hex = float_hex[:10] + hex(int(float_hex[10],16) + 1)[2] + "0000000"

    else:
        float_hex = float_hex[:11] + "0000000"
    return float_hex


# retorne Type.INT, etc para fazer checagem de tipos
class Type:
    VOID = "void"
    INT = "int"
    FLOAT = "float"
    STRING = "char *"

def llvm_type(tyype):
    if tyype == Type.VOID:
        return "void"
    if tyype == Type.INT:
        return "i32"
    if tyype == Type.FLOAT:
        return "float"


# This class defines a complete generic visitor for a parse tree produced by GrammarParser.
class GrammarCheckerVisitor(ParseTreeVisitor):
    ids_defined = {} # armazenar informações necessárias para cada identifier definido
    inside_what_function = ""
    next_ir_register = 0
    func_count = {}
    in_expr = []
    global_var = []

    # Visit a parse tree produced by GrammarParser#fiile.
    def visitFiile(self, ctx:GrammarParser.FiileContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#function_definition.
    def visitFunction_definition(self, ctx:GrammarParser.Function_definitionContext):
        tyype = ctx.tyype().getText()
        name = ctx.identifier().getText()
        params = self.visit(ctx.arguments())

        cte_value = None
        ir_register = None
        self.ids_defined[name] = tyype, params, cte_value, ir_register
        self.func_count[name] = 0
        self.inside_what_function = name
        self.next_ir_register = len(params) + 1

        #print function definiton
        print('define ' + str(llvm_type(tyype)) + ' @'+name +' (', end="")

        for i, p in enumerate(params):
            if(i < len(params)-1):
                print( str(llvm_type(p[0]))+' %'+ str(p[2])+',', end="")
            else:
                print( str(llvm_type(p[0]))+' %'+ str(p[2]), end="")
            self.func_count[name] = i+1
        print(') {')
        self.print_arg(params)
        self.visit(ctx.body())
        print('}')
        return


    # Visit a parse tree produced by GrammarParser#body.
    def visitBody(self, ctx:GrammarParser.BodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#statement.
    def visitStatement(self, ctx:GrammarParser.StatementContext):
        if ctx.RETURN() != None:
            #ret i32 %4

            token = ctx.RETURN().getPayload()
            function_type, params, cte_value, ir_register = self.ids_defined[self.inside_what_function]


            if ctx.expression() != None:
                tyype, cte_value, ir_register = self.visit(ctx.expression())
                if function_type == Type.INT and tyype == Type.FLOAT:
                    err("WARNING: possible loss of information returning float expression from int function '" + self.inside_what_function + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")
                elif function_type != Type.VOID and tyype == Type.VOID:
                    err("ERROR: trying to return void expression from function '" + self.inside_what_function + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")
                    exit(-1)
                elif function_type == Type.VOID and tyype != Type.VOID:
                    err("ERROR: trying to return a non void expression from void function '" + self.inside_what_function + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")
                    exit(-1)
            elif function_type != Type.VOID:
                err("ERROR: trying to return void expression from function '" + self.inside_what_function + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")
                exit(-1)

            if (function_type == Type.VOID):
                print('   ' +'ret ' + str(llvm_type(function_type)))
            else:
                if cte_value == None:
                    print('   ' +'ret ' + str(llvm_type(function_type)) +' %'+ str(self.func_count[ self.inside_what_function]))
                else:
                    print('   ' +'ret ' + str(llvm_type(function_type)) +' '+ str(cte_value if tyype == Type.INT else float_to_hex(cte_value)))


        else:
            self.visitChildren(ctx)
        return


    # Visit a parse tree produced by GrammarParser#if_statement.
    def visitIf_statement(self, ctx:GrammarParser.If_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#else_statement.
    def visitElse_statement(self, ctx:GrammarParser.Else_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#for_loop.
    def visitFor_loop(self, ctx:GrammarParser.For_loopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#for_initializer.
    def visitFor_initializer(self, ctx:GrammarParser.For_initializerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#for_condition.
    def visitFor_condition(self, ctx:GrammarParser.For_conditionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#for_step.
    def visitFor_step(self, ctx:GrammarParser.For_stepContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#variable_definition.
    def visitVariable_definition(self, ctx:GrammarParser.Variable_definitionContext):
        tyype = ctx.tyype().getText()
        ir_register = None

        # identifiers
        is_global = self.inside_what_function==''
        for i in range(len(ctx.identifier())):
            name = ctx.identifier(i).getText()
            token = ctx.identifier(i).IDENTIFIER().getPayload()
            if is_global:
                #print(name)
                self.global_var += [name]


            #%a = alloca i32, align 4
            if ctx.expression(i) != None:
                if not is_global:
                    print('   ' +'%'+name+ ' = alloca ' + str(llvm_type(tyype)) + ', align 4')
                expr_type, cte_value, ir_register = self.visit(ctx.expression(i))
                if is_global:
                    print('@'+name+'= global '+ str(llvm_type(expr_type))+' '+str(cte_value))
                if expr_type == Type.FLOAT:
                    if(cte_value != None):
                        if not is_global:
                            print('   ' +'store ' + str(llvm_type(expr_type)) + ' ' +str(float_to_hex(cte_value)) + ', '+ str(llvm_type(expr_type)) + '* %' + name+ ', align 4')
                    else:
                        if (self.func_count[self.inside_what_function] == None):
                            self.func_count[self.inside_what_function] = 1
                        if not is_global:
                            print('   ' +'store ' + str(llvm_type(expr_type)) + ' %' + str(self.func_count[self.inside_what_function]) + ', '+ str(llvm_type(expr_type)) + '* %' + name+ ', align 4')
                       #store float %1, float* %k, align 4
                else:
                    if not is_global:
                        print('   ' +'store ' + str(llvm_type(expr_type)) + ' ' + str(cte_value) + ', '+ str(llvm_type(expr_type)) + '* %' + name+ ', align 4')



                if expr_type == Type.VOID:
                    err("ERROR: trying to assign void expression to variable '" + name + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")
                    exit(-1)
                elif expr_type == Type.FLOAT and tyype == Type.INT:
                    err("WARNING: possible loss of information assigning float expression to int variable '" + name + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")
            else:
                # unitialized variables now get value 0
                cte_value = 0
                ir_register = None

            self.ids_defined[name] = tyype, -1, cte_value, ir_register # -1 means not a array, therefore no length here (vide 15 lines below)

        # arrays
        for i in range(len(ctx.array())):
            name = ctx.array(i).identifier().getText()
            token = ctx.array(i).identifier().IDENTIFIER().getPayload()

            array_length, _ = self.visit(ctx.array(i))
            if ctx.array_literal(i) != None:
                expr_types, cte_values_array, ir_registers_array = self.visit(ctx.array_literal(i))
                for j in range(len(expr_types)):
                    if expr_types[j] == Type.VOID:
                        err("ERROR: trying to initialize void expression to array '" + name + "' at index " + str(j) + " of array literal in line " + str(token.line) + " and column " + str(token.column) + "\n")
                        exit(-1)
                    elif expr_types[j] == Type.FLOAT and tyype == Type.INT:
                        err("WARNING: possible loss of information initializing float expression to int array '" + name + "' at index " + str(j) + " of array literal in line " + str(token.line) + " and column " + str(token.column) + "\n")
            else:
                # unitialized variables now get value 0
                cte_values_array = [0] * array_length
                ir_registers_array = [None] * array_length
            self.ids_defined[name] = tyype, array_length, cte_values_array, ir_registers_array
        print(" ")

        return


    # Visit a parse tree produced by GrammarParser#variable_assignment.
    def visitVariable_assignment(self, ctx:GrammarParser.Variable_assignmentContext):
        op = ctx.OP.text
        # identifier assignment
        if ctx.identifier() != None:
            name = ctx.identifier().getText()
            token = ctx.identifier().IDENTIFIER().getPayload()
            #print('name',name)
            try:
                tyype, _, cte_value, ir_register = self.ids_defined[name]

            except:
                err("ERROR: undefined variable '" + name + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")
                exit(-1)
                return

        # array assignment
        else:
            name = ctx.array().identifier().getText()
            token = ctx.array().identifier().IDENTIFIER().getPayload()
            try:
                tyype, array_length, cte_values_array, ir_registers_array = self.ids_defined[name]
            except:
                err("ERROR: undefined array '" + name + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")
                exit(-1)
            array_index_cte, array_index_ir = self.visit(ctx.array())
            if array_index_cte == None:
                cte_value = None
            else:
                if array_index_cte < 0 or array_index_cte >= array_length:
                    err("ERROR: array '" + name + "' index out of range in line " + str(token.line) + " and column " + str(token.column) + "\n")
                    exit(-1)
                else:
                    cte_value = cte_values_array[array_index_cte]
                    ir_register = ir_registers_array[array_index_cte]


        if op == '++' or op == '--':
            if cte_value != None:
                if op == '++':
                    cte_value += 1
                elif op == '--':
                    cte_value -= 1
            else:
                cte_value = 1
            
            if op == '++':
                self.func_count[self.inside_what_function] += 1
                ir_register = self.func_count[self.inside_what_function]
                print('   ' +"%"+str(ir_register)+" = load "+str(llvm_type(tyype))+", "+str(llvm_type(tyype))+"* %"+str(name)+", align 4")
                if tyype == Type.INT or tyype == Type.FLOAT:
                    ir_register += 1
                    print('   ' +"%"+str(ir_register)+" = add "+str(llvm_type(tyype))+" %"+str(self.func_count[self.inside_what_function])+", "+ str(cte_value))

                print('   ' +'store ' + str(llvm_type(tyype)) + ' %' + str(ir_register) + ', '+ str(llvm_type(tyype)) + '* %' + name+ ', align 4')
            cte_value += 1
            self.func_count[self.inside_what_function] = ir_register



        else:
            expr_type, expr_cte_value, expr_ir_register = self.visit(ctx.expression())
            self.in_expr = []
            if expr_type == Type.VOID:
                err("ERROR: trying to assign void expression to variable '" + name + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")
                exit(-1)
            elif expr_type == Type.FLOAT and tyype == Type.INT:
                err("WARNING: possible loss of information assigning float expression to int variable '" + name + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")

            if op == '=':
                cte_value = expr_cte_value
            elif op == '+=':
                self.func_count[self.inside_what_function] += 1
                ir_register = self.func_count[self.inside_what_function]
                print('   ' +"%"+str(ir_register)+" = load "+str(llvm_type(tyype))+", "+str(llvm_type(tyype))+"* %"+str(name)+", align 4")
                if tyype == Type.INT:
                    ir_register += 1
                    print('   ' +"%"+str(ir_register)+" = add "+str(llvm_type(tyype))+" %"+str(ir_register)+", "+('%'+str(expr_ir_register) if expr_ir_register != None else str(expr_cte_value)))
                elif tyype == Type.FLOAT:
                    ir_register += 1
                    print('   ' +"%"+str(ir_register)+" = fadd "+str(llvm_type(tyype))+" %"+str(ir_register)+", "+('%'+str(expr_ir_register) if expr_ir_register != None else str(expr_cte_value)))

                print('   ' +'store ' + str(llvm_type(expr_type)) + ' %' + str(ir_register) + ', '+ str(llvm_type(tyype)) + '* %' + name+ ', align 4')
                if cte_value != None and expr_cte_value != None:
                        cte_value += expr_cte_value

            elif op == '-=':
                self.func_count[self.inside_what_function] += 1
                ir_register = self.func_count[self.inside_what_function]
                print('   ' +"%"+str(ir_register)+" = load "+str(llvm_type(tyype))+", "+str(llvm_type(tyype))+"* %"+str(name)+", align 4")
                if tyype == Type.INT:
                    ir_register += 1
                    print('   ' +"%"+str(ir_register)+" = sub "+str(llvm_type(tyype))+" %"+str(ir_register)+", "+('%'+str(expr_ir_register) if expr_ir_register != None else str(expr_cte_value)))
                elif tyype == Type.FLOAT:
                    ir_register += 1
                    print('   ' +"%"+str(ir_register)+" = fsub "+str(llvm_type(tyype))+" %"+str(ir_register)+", "+('%'+str(expr_ir_register) if expr_ir_register != None else str(expr_cte_value)))

                print('   ' +'store ' + str(llvm_type(expr_type)) + ' %' + str(ir_register) + ', '+ str(llvm_type(tyype)) + '* %' + name+ ', align 4')
                if cte_value != None and expr_cte_value != None:
                    cte_value -= expr_cte_value
            elif op == '*=':
                self.func_count[self.inside_what_function] += 1
                ir_register = self.func_count[self.inside_what_function]
                print('   ' +"%"+str(ir_register)+" = load "+str(llvm_type(tyype))+", "+str(llvm_type(tyype))+"* %"+str(name)+", align 4")
                if tyype == Type.INT:
                    ir_register += 1
                    print('   ' +"%"+str(ir_register)+" = mul "+str(llvm_type(tyype))+" %"+str(ir_register)+", "+('%'+str(expr_ir_register) if expr_ir_register != None else str(expr_cte_value)))
                elif tyype == Type.FLOAT:
                    ir_register += 1
                    print('   ' +"%"+str(ir_register)+" = fmul "+str(llvm_type(tyype))+" %"+str(ir_register)+", "+('%'+str(expr_ir_register) if expr_ir_register != None else str(expr_cte_value)))

                print('   ' +'store ' + str(llvm_type(expr_type)) + ' %' + str(ir_register) + ', '+ str(llvm_type(tyype)) + '* %' + name+ ', align 4')
                if cte_value != None and expr_cte_value != None:
                    cte_value *= expr_cte_value
            elif op == '/=':
                self.func_count[self.inside_what_function] += 1
                ir_register = self.func_count[self.inside_what_function]
                print('   ' +"%"+str(ir_register)+" = load "+str(llvm_type(tyype))+", "+str(llvm_type(tyype))+"* %"+str(name)+", align 4")
                if tyype == Type.INT:
                    ir_register += 1
                    print('   ' +"%"+str(ir_register)+" = sdiv "+str(llvm_type(tyype))+" %"+str(ir_register)+", "+('%'+str(expr_ir_register) if expr_ir_register != None else str(expr_cte_value)))
                elif tyype == Type.FLOAT:
                    ir_register += 1
                    print('   ' +"%"+str(ir_register)+" = fdiv "+str(llvm_type(tyype))+" %"+str(ir_register)+", "+('%'+str(expr_ir_register) if expr_ir_register != None else str(expr_cte_value)))

                print('   ' +'store ' + str(llvm_type(expr_type)) + ' %' + str(ir_register) + ', '+ str(llvm_type(tyype)) + '* %' + name+ ', align 4')
                if cte_value != None and expr_cte_value != None:
                    cte_value /= expr_cte_value
            self.func_count[self.inside_what_function] = ir_register

        if ctx.identifier() != None:
            self.ids_defined[name] = tyype, -1, cte_value, ir_register
            #print(self.ids_defined[name])
           # print(self.visit(ctx.identifier()))
        else: # array
            if array_index_cte != None:
                cte_values_array[array_index_cte] = cte_value
                ir_registers_array[array_index_cte] = ir_register
            self.ids_defined[name] = tyype, array_length, cte_values_array, ir_registers_array
        print(" ")

        return


    # Visit a parse tree produced by GrammarParser#expression.
    def visitExpression(self, ctx:GrammarParser.ExpressionContext):
        tyype = Type.VOID
        cte_value = None
        ir_register = None

        if len(ctx.expression()) == 0:

            if ctx.integer() != None:
                tyype = Type.INT
                cte_value = int(ctx.integer().getText())

            elif ctx.floating() != None:
                tyype = Type.FLOAT
                cte_value = float(ctx.floating().getText())

            elif ctx.string() != None:
                tyype = Type.STRING

            elif ctx.identifier() != None:
                name = ctx.identifier().getText()
                try:
                    tyype, val, cte_value, ir_register = self.ids_defined[name]
                except:
                    token = ctx.identifier().IDENTIFIER().getPayload()
                    err("ERROR: undefined variable '" + name + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")
                    exit(-1)
                if (not name in self.in_expr and cte_value == None) or name in self.global_var:
                    if self.func_count[self.inside_what_function] == None:
                        self.func_count[self.inside_what_function] = 1


                    self.func_count[self.inside_what_function] += 1
                    print('   ' +"%"+str(self.func_count[self.inside_what_function])+" = load "+str(llvm_type(tyype))+", "+str(llvm_type(tyype))+"* %"+str(name)+", align 4")
                    #print(val)
                    self.in_expr += [name]
                    ir_register = self.func_count[self.inside_what_function]
                    cte_value = None if name in self.global_var else cte_value
                    self.ids_defined[name] = tyype, val, cte_value, ir_register
                    #print(self.in_expr)


            elif ctx.array() != None:
                name = ctx.array().identifier().getText()
                try:
                    tyype, array_length, cte_values_array, ir_registers_array = self.ids_defined[name]
                except:
                    token = ctx.array().identifier().IDENTIFIER().getPayload()
                    err("ERROR: undefined array '" + name + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")
                    exit(-1)

                array_index_cte, array_index_ir = self.visit(ctx.array())
                if array_index_cte != None:
                    if array_index_cte < 0 or array_index_cte >= array_length:
                        err("ERROR:  array '" + name + "' index out of bounds in line " + str(token.line) + " and column " + str(token.column) + "\n")
                        exit(-1)
                    else:
                        cte_value = cte_values_array[array_index_cte]
                        ir_register = ir_registers_array[array_index_cte]

            elif ctx.function_call() != None:
                tyype, cte_value, ir_register, name, params = self.visit(ctx.function_call())

                if(self.func_count[name] == None):
                    self.func_count[name] = 1
                # params: pares = tipos, ímpares = valores
                #print('ir '+ str(self.next_ir_register))

                if(tyype == Type.VOID):
                    print('   ' +'call',tyype + ' @'+name +" (",end="")

                else:
                    self.func_count[self.inside_what_function] += 1
                    print('   ' +'%'+ str(self.func_count[self.inside_what_function]) +' = call',tyype + ' @'+name +" (",end="")
                    self.func_count[name] = self.func_count[name] + 1
                    ir_register = self.func_count[self.inside_what_function]

                    #%1 = call float @ResDiv(float 0x4079000000000000, float 0x4072c00000000000)

                for i, p in enumerate(params):
                    if(i < len(params)-1):
                        if(p[0] == Type.FLOAT):
                            print('   ' + str(llvm_type(p[0]))+' '+ str(float_to_hex(p[1]))+', ', end="")
                        else:
                            print('   ' + str(llvm_type(p[0]))+' '+ str(p[1])+', ', end="")
                    else:
                        if(p[0] == Type.FLOAT):
                            print('   ' + str(llvm_type(p[0]))+' '+ str(float_to_hex(p[1])), end="")
                        else:
                            print('   ' + str(llvm_type(p[0]))+' '+ str(p[1]), end="")
                print(')')



               # print('aqui ',params)
                #print('call', tyype +' @' + name , + str(llvm_type(tyype)) + ' @'+name +' (', end="")
                #call void @splash(i32 8)

        elif len(ctx.expression()) == 1:

            if ctx.OP != None: #unary operators
                text = ctx.OP.text
                token = ctx.OP
                tyype, cte_value, ir_register = self.visit(ctx.expression(0))
                #print(text,cte_value)
                if tyype == Type.VOID:
                    err("ERROR: unary operator '" + text + "' used on type void in line " + str(token.line) + " and column " + str(token.column) + "\n")
                    exit(-1)
                
                elif cte_value != None:
                    if text == '-':
                        cte_value = -cte_value
                   
                if cte_value == None:
                    cte_value = 0
                    self.func_count[self.inside_what_function] += 1
                    print('   ' +"%"+str(self.func_count[self.inside_what_function])+" = sub "+str(llvm_type(tyype))+" "+str(cte_value)+(', %'+str(ir_register)))
                    #%5 = sub i32 0, %4
            else: # parentheses
                tyype, cte_value, ir_register = self.visit(ctx.expression(0))


        elif len(ctx.expression()) == 2: # binary operators
            text = ctx.OP.text
            token = ctx.OP
            left_type, left_cte_value, left_ir_register = self.visit(ctx.expression(0))
            right_type, right_cte_value, right_ir_register = self.visit(ctx.expression(1))
            if left_type == Type.VOID or right_type == Type.VOID:
                err("ERROR: binary operator '" + text + "' used on type void in line " + str(token.line) + " and column " + str(token.column) + "\n")
                exit(-1)

            if text == '*' or text == '/' or text == '+' or text == '-':
                if left_type == Type.FLOAT or right_type == Type.FLOAT:
                    tyype = Type.FLOAT
                else:
                    tyype = Type.INT

                

                if (left_type == Type.INT and right_type == Type.FLOAT) and (left_ir_register != None):
                    print('   ' +"%"+str(self.func_count[self.inside_what_function] + 1)+" = sitofp "+str(llvm_type(Type.INT))+" "+'%'+str(left_ir_register) + ' to float')
                    self.func_count[self.inside_what_function] += 1
                    ir_register = self.func_count[self.inside_what_function]
                    left_ir_register = ir_register
                    #%4 = sitofp i32 %3 to float
                

                if left_cte_value != None and right_cte_value != None:
                    if text == '*':
                        cte_value = left_cte_value * right_cte_value
                    elif text == '/':
                        cte_value = left_cte_value / right_cte_value
                    elif text == '+':
                        cte_value = left_cte_value + right_cte_value
                    elif text == '-':
                        cte_value = left_cte_value - right_cte_value
                else:
                    if text == '*':
                        if tyype == Type.INT:
                            self.func_count[self.inside_what_function] += 1
                            ir_register = self.func_count[self.inside_what_function]
                            print('   ' +"%"+str(ir_register)+" = mul "+str(llvm_type(tyype))+" "+('%'+str(left_ir_register) if left_ir_register != None else str(left_cte_value if left_type == Type.INT else left_cte_value))+", "+('%'+str(right_ir_register) if right_ir_register != None else str(right_cte_value if right_type == Type.INT else right_cte_value)))
                        elif tyype == Type.FLOAT:
                            self.func_count[self.inside_what_function] += 1
                            #print(ir_register)
                            ir_register = self.func_count[self.inside_what_function]
                            #print(ir_register)
                            print('   ' +"%"+str(ir_register)+" = fmul "+str(llvm_type(tyype))+" "+('%'+str(left_ir_register) if left_ir_register != None else str(left_cte_value if left_type == Type.INT else left_cte_value))+", "+('%'+str(right_ir_register) if right_ir_register != None else str(right_cte_value if right_type == Type.INT else right_cte_value)))
                    elif text == '/':
                        if tyype == Type.INT:
                            self.func_count[self.inside_what_function] += 1
                            ir_register = self.func_count[self.inside_what_function]
                            print('   ' +"%"+str(ir_register)+" = sdiv "+str(llvm_type(tyype))+" "+('%'+str(left_ir_register) if left_ir_register != None else str(left_cte_value if left_type == Type.INT else left_cte_value))+", "+('%'+str(right_ir_register) if right_ir_register != None else str(right_cte_value if right_type == Type.INT else right_cte_value)))
                        elif tyype == Type.FLOAT:
                            self.func_count[self.inside_what_function] += 1
                            ir_register = self.func_count[self.inside_what_function]
                            print('   ' +"%"+str(ir_register)+" = fdiv "+str(llvm_type(tyype))+" "+('%'+str(left_ir_register) if left_ir_register != None else str(left_cte_value if left_type == Type.INT else left_cte_value))+", "+('%'+str(right_ir_register) if right_ir_register != None else str(right_cte_value if right_type == Type.INT else right_cte_value)))
                    elif text == '+':
                        if tyype == Type.INT:
                            self.func_count[self.inside_what_function] += 1
                            ir_register = self.func_count[self.inside_what_function]
                            print('   ' +"%"+str(ir_register)+" = add "+str(llvm_type(tyype))+" "+('%'+str(left_ir_register) if left_ir_register != None else str(left_cte_value if left_type == Type.INT else left_cte_value))+", "+('%'+str(right_ir_register) if right_ir_register != None else str(right_cte_value if right_type == Type.INT else right_cte_value)))
                        elif tyype == Type.FLOAT:
                            self.func_count[self.inside_what_function] += 1
                            ir_register = self.func_count[self.inside_what_function]
                            print('   ' +"%"+str(ir_register)+" = fadd "+str(llvm_type(tyype))+" "+('%'+str(left_ir_register) if left_ir_register != None else str(left_cte_value if left_type == Type.INT else left_cte_value))+", "+('%'+str(right_ir_register) if right_ir_register != None else str(right_cte_value if right_type == Type.INT else right_cte_value)))
                    elif text == '-':
                        if tyype == Type.INT:
                            self.func_count[self.inside_what_function] += 1
                            ir_register = self.func_count[self.inside_what_function]
                            print('   ' +"%"+str(ir_register)+" = sub "+str(llvm_type(tyype))+" "+('%'+str(left_ir_register) if left_ir_register != None else str(left_cte_value if left_type == Type.INT else left_cte_value))+", "+('%'+str(right_ir_register) if right_ir_register != None else str(right_cte_value if right_type == Type.INT else right_cte_value)))
                        elif tyype == Type.FLOAT:
                            self.func_count[self.inside_what_function] += 1
                            ir_register = self.func_count[self.inside_what_function]
                            print('   ' +"%"+str(ir_register)+" = fsub "+str(llvm_type(tyype))+" "+('%'+str(left_ir_register) if left_ir_register != None else str(left_cte_value if left_type == Type.INT else left_cte_value))+", "+('%'+str(right_ir_register) if right_ir_register != None else str(right_cte_value if right_type == Type.INT else right_cte_value)))
                    cte_value = None
            else:
                tyype = Type.INT
                if left_cte_value != None and right_cte_value != None:
                    if text == '<':
                        if left_cte_value < right_cte_value:
                            cte_value = 1
                        else:
                            cte_value = 0
                    elif text == '>':
                        if left_cte_value > right_cte_value:
                            cte_value = 1
                        else:
                            cte_value = 0
                    elif text == '==':
                        if left_cte_value == right_cte_value:
                            cte_value = 1
                        else:
                            cte_value = 0
                    elif text == '!=':
                        if left_cte_value != right_cte_value:
                            cte_value = 1
                        else:
                            cte_value = 0
                    elif text == '<=':
                        if left_cte_value <= right_cte_value:
                            cte_value = 1
                        else:
                            cte_value = 0
                    elif text == '>=':
                        if left_cte_value >= right_cte_value:
                            cte_value = 1
                        else:
                            cte_value = 0
                else:
                    cte_value = None
        return tyype, cte_value, ir_register

    # Visit a parse tree produced by GrammarParser#array.
    def visitArray(self, ctx:GrammarParser.ArrayContext):
        tyype, cte_value, ir_register = self.visit(ctx.expression())
        if tyype != Type.INT:
            token = ctx.identifier().IDENTIFIER().getPayload()
            err("ERROR: array expression must be an integer, but it is " + str(tyype) + " in line " + str(token.line) + " and column " + str(token.column) + "\n")
            exit(-1)
        return cte_value, ir_register


    # Visit a parse tree produced by GrammarParser#array_literal.
    def visitArray_literal(self, ctx:GrammarParser.Array_literalContext):
        types_array = []
        cte_values_array = []
        ir_registers_array = []
        for i in range(len(ctx.expression())):
            tyype, cte_value, ir_register = self.visit(ctx.expression(i))
            types_array += [tyype]
            cte_values_array += [cte_value]
            ir_registers_array += [ir_register]
        return types_array, cte_values_array, ir_registers_array


    # Visit a parse tree produced by GrammarParser#function_call.
    def visitFunction_call(self, ctx:GrammarParser.Function_callContext):
        name = ctx.identifier().getText()
        token = ctx.identifier().IDENTIFIER().getPayload()
        args_array = []

        try:
            tyype, args, cte_value, ir_register = self.ids_defined[name]
            if len(args) != len(ctx.expression()):
                err("ERROR: incorrect number of parameters for function '" + name + "' in line " + str(token.line) + " and column " + str(token.column) + ". Expecting " + str(len(args)) + ", but " + str(len(ctx.expression())) + " were given" + "\n")
                exit(-1)
        except:
            err("ERROR: undefined function '" + name + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")
            exit(-1)

        for i in range(len(ctx.expression())):
            arg_type, arg_cte_value, arg_ir_register = self.visit(ctx.expression(i))
            #print('args', arg_type, arg_cte_value)
            args_array.append([arg_type, arg_cte_value])
            if i < len(args):
                if arg_type == Type.VOID:
                    err("ERROR: void expression passed as parameter " + str(i) + " of function '" + name + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")
                    exit(-1)
                elif arg_type == Type.FLOAT and args[i] == Type.INT:
                    err("WARNING: possible loss of information converting float expression to int expression in parameter " + str(i) + " of function '" + name + "' in line " + str(token.line) + " and column " + str(token.column) + "\n")
        #print('args array', args_array)
        return tyype, cte_value, ir_register, name, args_array


    # Visit a parse tree produced by GrammarParser#arguments.
    def visitArguments(self, ctx:GrammarParser.ArgumentsContext):
        params = []
        cte_value = None
        for i in range(len(ctx.identifier())):
            tyype = ctx.tyype(i).getText()
            name = ctx.identifier(i).getText()
            ir_register = i
            self.ids_defined[name] = tyype, -1, cte_value, ir_register
            #print('aqui 2 ',self.ids_defined[name])
            params.append([tyype, name, ir_register])

        return params


    # Visit a parse tree produced by GrammarParser#tyype.
    def visitTyype(self, ctx:GrammarParser.TyypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#integer.
    def visitInteger(self, ctx:GrammarParser.IntegerContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#floating.
    def visitFloating(self, ctx:GrammarParser.FloatingContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#string.
    def visitString(self, ctx:GrammarParser.StringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by GrammarParser#identifier.
    def visitIdentifier(self, ctx:GrammarParser.IdentifierContext):
        return self.visitChildren(ctx)

    def print_arg(self, params):
        cte_value = None
        for p in params:
            tyype, name, ir_register = p[0], p[1], p[2]

            print('   ' +'%'+name+ ' = alloca ' + str(llvm_type(tyype)) + ', align 4')
            print('   ' +'store ' + str(llvm_type(tyype)) + ' %' + str(ir_register) + ', '+ str(llvm_type(tyype)) + '* %' + name+ ', align 4')
        print(" ")

# warning: the use of uninitialized variables is not being warned!