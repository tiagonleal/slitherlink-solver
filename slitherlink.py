#!/usr/bin/python3
# slitherlink.py: Template para implementação do projeto de Inteligência Artificial 2025/2026.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes sugeridas, podem acrescentar outras que considerem pertinentes.

# Grupo 33:
# 114743 Pedro Sousa
# 113799 Tiago Leal


import random, copy
from sys import stdin
from collections import defaultdict

import utils
from utils import *

from search import (
    Problem,
    Node,
    astar_search,
    breadth_first_tree_search,
    depth_first_tree_search,
    greedy_search,
    recursive_best_first_search,
)


class SlitherlinkState:
    state_id = 0


    def __init__(self, board):
        self.board = board
        self.id = SlitherlinkState.state_id
        SlitherlinkState.state_id += 1
    
    def __lt__(self, other):
        return self.id < other.id

    # TODO: outros metodos da classe

class Board:
    """Representação interna de um tabuleiro de Slitherlink."""

    UNKNOWN   = 0
    ACTIVE    = 1
    FORBIDDEN = 2

    def __init__(self, hints):
        self.hints = hints
        self.rows = len(hints)
        self.valid = True
        if (self.rows > 0): self.cols = len(hints[0]) 
        else: self.cols = 0

        self.hor_edges = [self.cols * [Board.UNKNOWN] for _ in range(self.rows + 1)]
        self.ver_edges = [(self.cols + 1 )* [Board.UNKNOWN] for _ in range(self.rows)]

    def static_rules(self):
        """Altera o tabuleiro inicial conforme as regras iniciais de resolução"""
        
        corners = [(0, 0, 0, 0, 0, 0),
                   (0, self.cols - 1, 0, self.cols - 1, 0, self.cols), 
                   (self.rows - 1, 0, self.rows, 0, self.rows - 1, 0),
                   (self.rows - 1, self.cols - 1, self.rows, self.cols - 1, self.rows - 1, self.cols)]
        
        #Verificar cantos
        for cr, cc, rh, ch, rv, cv in corners:

            #Se tiver um 3 num canto, preencher no canto com linhas
            if (self.hints[cr][cc] == 3):
                self.hor_edges[rh][ch] = Board.ACTIVE
                self.ver_edges[rv][cv] = Board.ACTIVE

            #Se tiver um 1 num canto, preencher o canto com cruzes
            elif (self.hints[cr][cc] == 1):
                self.hor_edges[rh][ch] = Board.FORBIDDEN
                self.ver_edges[rv][cv] = Board.FORBIDDEN
        
        for r in range(self.rows):
            for c in range(self.cols):

                #Em todos os 0's preencher com cruzes à volta
                if (self.hints[r][c] == 0):
                    self.hor_edges[r][c] = Board.FORBIDDEN
                    self.hor_edges[r + 1][c] = Board.FORBIDDEN
                    self.ver_edges[r][c] = Board.FORBIDDEN
                    self.ver_edges[r][c + 1] = Board.FORBIDDEN

                elif (self.hints[r][c] == 3):
                    #Se o 3 tiver um 3 à direita, preencher com linhas verticais
                    if (c < self.cols - 1 and self.hints[r][c + 1] == 3):
                        self.ver_edges[r][c] = Board.ACTIVE
                        self.ver_edges[r][c + 1] = Board.ACTIVE
                        self.ver_edges[r][c + 2] = Board.ACTIVE

                    #Se o 3 tiver um 3 em baixo, preencher com linhas horizontais
                    if (r < self.rows - 1 and self.hints[r + 1][c] == 3):
                        self.hor_edges[r][c] = Board.ACTIVE
                        self.hor_edges[r + 1][c] = Board.ACTIVE
                        self.hor_edges[r + 2][c] = Board.ACTIVE

                    #Se o 3 tiver um 3 na diagonal inferior direita
                    if (c < self.cols - 1 and r < self.rows - 1 
                        and self.hints[r + 1][c + 1] == 3):
                        self.ver_edges[r][c] = Board.ACTIVE
                        self.hor_edges[r][c] = Board.ACTIVE
                        self.ver_edges[r + 1][c + 2] = Board.ACTIVE
                        self.hor_edges[r + 2][c + 1] = Board.ACTIVE

                    #Se o 3 tiver um 3 na diagonal inferior esquerda
                    if (c > 0 and r < self.rows - 1 and self.hints[r + 1][c - 1] == 3):
                        self.ver_edges[r][c + 1] = Board.ACTIVE
                        self.hor_edges[r][c] = Board.ACTIVE
                        self.ver_edges[r + 1][c - 1] = Board.ACTIVE
                        self.hor_edges[r + 2][c - 1] = Board.ACTIVE

                    #Se o 3 tiver um 0 na diagonal inferior direita
                    if (c < self.cols - 1 and r < self.rows - 1 
                        and self.hints[r + 1][c + 1] == 0):
                        self.ver_edges[r][c + 1] = Board.ACTIVE
                        self.hor_edges[r + 1][c] = Board.ACTIVE

                    #Se o 3 tiver um 0 na diagonal inferior esquerda
                    if (c > 0 and r < self.rows - 1 and self.hints[r + 1][c - 1] == 0):
                        self.ver_edges[r][c] = Board.ACTIVE
                        self.hor_edges[r + 1][c] = Board.ACTIVE

                    #Se o 3 tiver um 0 na diagonal superior esquerda
                    if (c > 0 and r > 0  and self.hints[r - 1][c - 1] == 0):
                        self.ver_edges[r][c] = Board.ACTIVE
                        self.hor_edges[r][c] = Board.ACTIVE

                    #Se o 3 tiver um 0 na diagonal superior direita
                    if (c < self.cols - 1 and r > 0 and self.hints[r - 1][c + 1] == 0):
                        self.ver_edges[r][c + 1] = Board.ACTIVE
                        self.hor_edges[r][c] = Board.ACTIVE

    def adjacent_cell(self, cell:tuple) -> list:
        """Devolve uma lista das células que fazem
        fronteira com a célula enviada no argumento"""
        row = cell[0]
        col = cell[1]

        adjacent = []

        # Top
        if (row > 0):
            adjacent.append((row - 1, col))

        # Bottom
        if (row < self.rows - 1):
            adjacent.append((row + 1, col))

        # Left
        if (col > 0):
            adjacent.append((row, col - 1))

        # Right
        if (col < self.cols - 1):
            adjacent.append((row, col + 1))

        return adjacent

    def get_cell_edges(self, row:int, column:int) -> list:
        """Devolve os arestas da célula enviada no argumento"""

        return [    
            ('h', row, column),          # Top
            ('h', row + 1, column),      # Bottom
            ('v', row, column),          # Left
            ('v', row, column + 1)       # Right
        ]
    
    def get_edge_vertices(self, edge_type: str, row: int, col: int) -> list:
        "Devolve os vértices de uma aresta"
        if (edge_type == 'h'):
            return [(row, col), (row, col + 1)]

        if (edge_type == 'v'):
            return [(row, col), (row + 1, col)]

        return None

    def get_active_edges(self, row:int, column:int) -> int:
        """Devolve o número de arestas ativas"""             
        nbr_act_edges = 0

        if (self.hor_edges[row][column] == Board.ACTIVE): nbr_act_edges += 1
        if (self.hor_edges[row + 1][column] == Board.ACTIVE): nbr_act_edges += 1
        if (self.ver_edges[row][column] == Board.ACTIVE): nbr_act_edges += 1
        if (self.ver_edges[row][column + 1] == Board.ACTIVE): nbr_act_edges += 1
        
        return nbr_act_edges
    
    def get_inactive_edges(self, row:int, column:int) -> int:
        """Devolve o número de arestas que não estão preenchidas"""
        nbr_inact_edges = 0

        if (self.hor_edges[row][column] == Board.UNKNOWN): nbr_inact_edges += 1
        if (self.hor_edges[row + 1][column] == Board.UNKNOWN): nbr_inact_edges += 1
        if (self.ver_edges[row][column] == Board.UNKNOWN): nbr_inact_edges += 1
        if (self.ver_edges[row][column + 1] == Board.UNKNOWN): nbr_inact_edges += 1
        
        return nbr_inact_edges

    def get_state_vertex_edges(self, row: int, column: int, edge_state: int, 
                               get_list = False) -> int:
        """Devolve o número de arestas que cumprem a condição 
           edge_state que tocam no vértice (row, column)."""

        nbr_act_edges = 0
        lista_arestas = []

        if (row > 0):
            if (self.ver_edges[row - 1][column] == edge_state):
                nbr_act_edges += 1
                lista_arestas.append(('v', row - 1, column))

        if (row < self.rows):
            if (self.ver_edges[row][column] == edge_state):
                nbr_act_edges += 1
                lista_arestas.append(('v', row, column))

        if (column > 0):
            if (self.hor_edges[row][column - 1] == edge_state):
                nbr_act_edges += 1
                lista_arestas.append(('h', row, column -1))

        if (column < self.cols):
            if (self.hor_edges[row][column] == edge_state):
                nbr_act_edges += 1
                lista_arestas.append(('h', row, column))

        if (get_list):
            return lista_arestas
        
        return nbr_act_edges
    
    def change_edge_state(self, type: str, row: int, col: int, state: int):
        """Muda o estado da aresta dada pelos argumentos type, row e col 
        para o estado dado pelo argumento state."""
        if (type == 'h'):
            self.hor_edges[row][col] = state
        if (type == 'v'):
            self.ver_edges[row][col] = state
    
    def clone(self):
        """Devolve uma cópia do tabuleiro, incluindo o estado de cada aresta 
        e o atributo valid."""
        new_board = Board(self.hints)

        new_board.valid = self.valid

        new_board.hor_edges = [row[:] for row in self.hor_edges]
        new_board.ver_edges = [row[:] for row in self.ver_edges]
        
        return new_board
    

    def has_premature_loop(self) -> bool:
        """Devolve True se houver um ciclo formado por arestas ACTIVE que não 
        inclua todas as arestas ACTIVE do tabuleiro ou se houver um ciclo formado
        por arestas ACTIVE que não cumpra as regras do jogo Devolve False caso contrário."""

        active_edges = set()
        for r in range(self.rows + 1):
            for c in range(self.cols):
                if (self.hor_edges[r][c] == Board.ACTIVE):
                    active_edges.add(('h', r, c))
        for r in range(self.rows):
            for c in range(self.cols + 1):
                if (self.ver_edges[r][c] == Board.ACTIVE):
                    active_edges.add(('v', r, c))
        
        if (not active_edges):
            return False

        visited = set()
        
        for start_edge in active_edges:
            if (start_edge in visited):
                continue
            
            stack = [start_edge]
            component = set()
            
            is_closed = True
            
            while stack:
                edge = stack.pop()
                if (edge in component):
                    continue
                    
                component.add(edge)
                visited.add(edge)
                
                tipo, r, c = edge
                if (tipo == 'h'):
                    vertices = [(r, c), (r, c + 1)]
                else:
                    vertices = [(r, c), (r + 1, c)]

                for vr, vc in vertices:
                    active_neighbors = self.get_state_vertex_edges(vr, vc, 
                                                                   Board.ACTIVE, 
                                                                   True)

                    if (len(active_neighbors) != 2):
                        is_closed = False

                    for neighbor in active_neighbors:
                        if (neighbor not in component):
                            stack.append(neighbor)
            
            if (is_closed):
                if (len(component) < len(active_edges)):
                    return True
                for r in range(self.rows):
                    for c in range(self.cols):
                        hint = self.hints[r][c]
                        if (hint != -1):
                            actives = self.get_active_edges(r, c)
                            if (actives != hint):
                                return True
        return False

    @staticmethod
    def parse_instance():
        """Lê o test do standard input (stdin) que é passado como argumento
        e retorna uma instância da classe Board.

        Por exemplo:
            $ python3 pipe.py < test-01.txt

            > from sys import stdin
            > line = stdin.readline().split()
        """
        hints = []

        line = stdin.readline()

        while line != "":
            values = line.split()

            if (values):
                row = []

                for value in values:
                    if (value == '.'):
                        row.append(-1)
                    else:
                        row.append(int(value))

                hints.append(row)

            line = stdin.readline()

        return Board(hints)

class Slitherlink(Problem):
    def __init__(self, board: Board, gui=None):
        """O construtor especifica o estado inicial."""
        SlitherlinkState.state_id = 0

        initial_state = SlitherlinkState(board)

        super().__init__(initial_state)

        board.static_rules()

        while(self.board_update(initial_state)):
            pass
        self.gui = gui


    def actions(self, state: SlitherlinkState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""

        board = state.board
        if (not board.valid):
            return []
        
        best_cell = None
        nbr_unknowns = 5

        # Procurar a célula numerada incompleta mais constrangida
        for r in range(board.rows):
            for c in range(board.cols):
                hint = board.hints[r][c]

                if (hint == -1):
                    continue

                unknowns = board.get_inactive_edges(r, c)

                if (unknowns > 0 and unknowns < nbr_unknowns):
                    nbr_unknowns = unknowns
                    best_cell = (r, c)

                if (nbr_unknowns == 1):
                        break
                
            if (nbr_unknowns == 1):
                        break
        # Se houver uma célula numerada incompleta,
        # escolher uma aresta UNKNOWN dessa célula

        if (best_cell is not None):
            r, c = best_cell

            for edge_type, edge_r, edge_c in board.get_cell_edges(r, c):
                if (edge_type == 'h'):
                    if (board.hor_edges[edge_r][edge_c] == Board.UNKNOWN):
                        return [('h', edge_r, edge_c, Board.ACTIVE), ('h', edge_r, 
                                                                      edge_c, 
                                                                      Board.FORBIDDEN)]

                elif (edge_type == 'v'):
                    if (board.ver_edges[edge_r][edge_c] == Board.UNKNOWN):
                        return [('v', edge_r, edge_c, Board.ACTIVE), ('v', edge_r, 
                                                                      edge_c, 
                                                                      Board.FORBIDDEN)]
                    
        # Se não houver células numeradas com arestas UNKNOWN, 
        # escolher uma aresta UNKNOWN que partilhe um vértice com uma aresta ACTIVE (continuação do loop)
        for r in range(board.rows + 1):
            for c in range(board.cols + 1):
                # Check if this vertex has exactly 1 active edge
                act_edge = board.get_state_vertex_edges(r, c, board.ACTIVE)
                unk_edges = board.get_state_vertex_edges(r, c, board.UNKNOWN, True)
                if (act_edge == 1 and len(unk_edges) > 0):
                    edge_type, edge_r, edge_c = unk_edges[0]
                    return [(edge_type, edge_r, edge_c, Board.ACTIVE), (edge_type, 
                                                                        edge_r, 
                                                                        edge_c, 
                                                                        Board.FORBIDDEN)]

        # Escolhe uma aresta UNKNOWN restante
        for r in range(board.rows + 1):
            for c in range(board.cols):
                if (board.hor_edges[r][c] == Board.UNKNOWN):
                    return [('h', r, c, Board.ACTIVE), ('h', r, c, Board.FORBIDDEN)]
        
        for r in range(board.rows):
            for c in range(board.cols + 1):
                if (board.ver_edges[r][c] == Board.UNKNOWN):
                    return [('v', r, c, Board.ACTIVE), ('v', r, c, Board.FORBIDDEN)]
        
        return []


    def result(self, state: SlitherlinkState, action):
        """Recebe um estado e uma ação e devolve o estado resultante de executar
        a ação sobre o estado passado como argumento. Se a ação é inválida, 
        retorna um estado igual ao estado passado como argumento"""

        new_board = state.board.clone()
        tipo, r, c, value = action

        if (tipo == 'h'):
            new_board.hor_edges[r][c] = value
        elif (tipo == 'v'):
            new_board.ver_edges[r][c] = value

        new_state = SlitherlinkState(new_board)

        while(self.board_update(new_state)):
            pass

        if (new_board.valid and new_board.has_premature_loop()):
            new_board.valid = False

        return new_state


    def board_update(self, state: SlitherlinkState):
        """Recebe o estado do tabuleiro e preenche as arestas que já são possíveis 
        completar, de acordo com as regras do jogo. Retorna True se o tabuleiro 
        foi atualizado, ou seja, se alguma aresta foi preenchida. Se o tabuleiro
        for considerado inválido, retorna False e coloca o atributo valid do tabuleiro a False."""
        
        board = state.board
        changed = 0
        for r in range(board.rows + 1):
            for c in range(board.cols + 1):
                act_edge = 0
                unk_edges_to_change = []

                if (r > 0):
                    val = board.ver_edges[r - 1][c]
                    if (val == Board.ACTIVE):
                        act_edge += 1
                    elif (val == Board.UNKNOWN):
                        unk_edges_to_change.append(('v', r - 1, c))

                if (r < board.rows):
                    val = board.ver_edges[r][c]
                    if (val == Board.ACTIVE):
                        act_edge += 1
                    elif (val == Board.UNKNOWN):
                        unk_edges_to_change.append(('v', r, c))

                if (c > 0):
                    val = board.hor_edges[r][c - 1]
                    if (val == Board.ACTIVE):
                        act_edge += 1
                    elif (val == Board.UNKNOWN):
                        unk_edges_to_change.append(('h', r, c - 1))

                if (c < board.cols):
                    val = board.hor_edges[r][c]
                    if (val == Board.ACTIVE):
                        act_edge += 1
                    elif (val == Board.UNKNOWN):
                        unk_edges_to_change.append(('h', r, c))

                unk_edge = len(unk_edges_to_change)
                unk_edge_list = unk_edges_to_change

                if (r < board.rows and c < board.cols):
                    hint = board.hints[r][c]
                    if (hint != -1):
                        actives = 0
                        unknowns = 0
                        
                        val = board.hor_edges[r][c]
                        if (val == Board.ACTIVE): actives += 1
                        elif (val == Board.UNKNOWN): unknowns += 1
                        
                        val = board.hor_edges[r + 1][c]
                        if (val == Board.ACTIVE): actives += 1
                        elif (val == Board.UNKNOWN): unknowns += 1
                        
                        val = board.ver_edges[r][c]
                        if (val == Board.ACTIVE): actives += 1
                        elif (val == Board.UNKNOWN): unknowns += 1
                        
                        val = board.ver_edges[r][c + 1]
                        if (val == Board.ACTIVE): actives += 1
                        elif (val == Board.UNKNOWN): unknowns += 1
                        
                        forbiddens = 4 - actives - unknowns

                        #Situação proibida
                        if (actives > hint or forbiddens > 4 - hint):
                            board.valid = False
                            return False

                        #Condicao preenchida, mas alguns ainda unknowns
                        if (actives == hint and unknowns > 0):
                            if (board.hor_edges[r][c] == Board.UNKNOWN):
                                board.hor_edges[r][c] = Board.FORBIDDEN
                                changed = 1
                            if (board.hor_edges[r + 1][c] == Board.UNKNOWN):
                                board.hor_edges[r + 1][c] = Board.FORBIDDEN
                                changed = 1
                            if (board.ver_edges[r][c] == Board.UNKNOWN):
                                board.ver_edges[r][c] = Board.FORBIDDEN
                                changed = 1
                            if (board.ver_edges[r][c + 1] == Board.UNKNOWN):
                                board.ver_edges[r][c + 1] = Board.FORBIDDEN
                                changed = 1

                        #Uknowns + active = condição
                        elif (unknowns > 0 and actives + unknowns == hint):
                            if (board.hor_edges[r][c] == Board.UNKNOWN):
                                board.hor_edges[r][c] = Board.ACTIVE
                                changed = 1
                            if (board.hor_edges[r + 1][c] == Board.UNKNOWN):
                                board.hor_edges[r + 1][c] = Board.ACTIVE
                                changed = 1
                            if (board.ver_edges[r][c] == Board.UNKNOWN):
                                board.ver_edges[r][c] = Board.ACTIVE
                                changed = 1
                            if (board.ver_edges[r][c + 1] == Board.UNKNOWN):
                                board.ver_edges[r][c + 1] = Board.ACTIVE
                                changed = 1

                if (act_edge >= 3):
                    board.valid = False
                    return False
                
                if (act_edge == 1 and unk_edge == 0):
                    board.valid = False
                    return False
                    
                if (act_edge == 2 and unk_edge > 0):
                    for type, row, col in unk_edge_list:
                        if (type == 'h'): board.hor_edges[row][col] = Board.FORBIDDEN
                        else: board.ver_edges[row][col] = Board.FORBIDDEN
                        changed = 1

                if (act_edge == 1 and unk_edge == 1):
                    type, row, col = unk_edge_list[0]
                    if (type == 'h'): board.hor_edges[row][col] = Board.ACTIVE
                    else: board.ver_edges[row][col] = Board.ACTIVE
                    changed = 1

                if (act_edge == 0 and unk_edge == 1):
                    type, row, col = unk_edge_list[0]
                    if (type == 'h'): board.hor_edges[row][col] = Board.FORBIDDEN
                    else: board.ver_edges[row][col] = Board.FORBIDDEN
                    changed = 1
                
                    

        if (changed == 1):
            return True
        else:
            return False

    def goal_test(self, state: SlitherlinkState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""

        board = state.board

        if (not board.valid):
            return False

        #Primeira verificação - todos os quadrados estão rodeados pelo número certo de linhas?
        for r in range(board.rows):
            for c in range(board.cols):
                hint = board.hints[r][c]
                if (hint != -1):
                    if (hint != board.get_active_edges(r, c)):
                        return False
                    

        #Segunda verificação - Cada vértice tem 0 ou 2 linhas ligadas

        for row in range(board.rows + 1):
            for column in range(board.cols + 1):
                active = board.get_state_vertex_edges(row, column, board.ACTIVE)

                if (active != 0 and active != 2):
                    return False


        #Terceira Verificação - Só há um loop

        found = 0
        start_edge = None
        for r in range(board.rows + 1):
            for c in range(board.cols):
                if (board.hor_edges[r][c] == Board.ACTIVE):
                    found += 1
                    if (start_edge == None):
                        start_edge = ('h', r, c)

        for r in range(board.rows):
            for c in range(board.cols + 1):
                if (board.ver_edges[r][c] == Board.ACTIVE):
                    found += 1
                    if (start_edge == None):
                        start_edge = ('v', r, c)
        if (not found):
            return False
        
        visited = set()
        to_visit = [start_edge]

        while (to_visit):
            current = to_visit.pop()

            if (current not in visited):
                tipo, r, c = current
                visited.add(current)

                if (tipo == 'h'):
                    vertices = [(r, c), (r, c + 1)]
                elif (tipo == 'v'):
                    vertices = [(r, c), (r + 1, c)]

                for current_row, current_column in vertices:
                    vizinhos = board.get_state_vertex_edges(current_row, 
                                                            current_column, 
                                                            board.ACTIVE, True)

                    for vizinho in vizinhos:
                        if (vizinho not in to_visit and vizinho not in visited):
                            to_visit.append(vizinho)

        return len(visited) == found

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        pass


if __name__ == "__main__":

    board = Board.parse_instance()

    problem = Slitherlink(board)

    solution_node = depth_first_tree_search(problem)

    if (solution_node is None):
        exit(1)

    solution_board = solution_node.state.board

    for r in range(solution_board.rows):
        output_row = ""

        for c in range(solution_board.cols):
            top = '1' if solution_board.hor_edges[r][c] == Board.ACTIVE else '0'
            right = '1' if solution_board.ver_edges[r][c + 1] == Board.ACTIVE else '0'
            bottom = '1' if solution_board.hor_edges[r + 1][c] == Board.ACTIVE else '0'
            left = '1' if solution_board.ver_edges[r][c] == Board.ACTIVE else '0'

            output_cell = top + right + bottom + left
            output_row += output_cell
            if (c < solution_board.cols - 1):
                output_row += '\t'

        print(output_row)