#!/usr/bin/env pypy3 -u
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import division
import importlib
import re
import sys
import time
import logging

import tools
import sunfish

from tools import WHITE, BLACK
#from xboard import Unbuffered, sunfish, input
from xboard import Unbuffered
sys.stdout = Unbuffered(sys.stdout)

def main():
    logging.basicConfig(filename='sunfish.log',level=logging.DEBUG)
    pos = tools.parseFEN(tools.FEN_INITIAL)
    searcher = sunfish.Searcher()
    forced = False
    color = WHITE
    our_time, opp_time = 1000, 1000 # time in centi-seconds
    show_thinking = True

    # print name of chess engine
    print('Sunfish')

    stack = []
    while True:
        if stack:
            smove = stack.pop()
        else: smove = input()

        logging.debug(smove)

        if smove == 'quit':
            break

        elif smove == 'uci':
            print('id name Sunfish')
            print('id author Thomas Ahle')
            print('uciok')

        elif smove == 'isready':
            print('readyok')

        elif smove == 'ucinewgame':
            stack.append('position fen ' + tools.FEN_INITIAL)

        elif smove.startswith('position fen'):
            params = smove.split(' ', 2)
            if params[1] == 'fen':
                fen = params[2]
                pos = tools.parseFEN(fen)
                color = WHITE if fen.split()[1] == 'w' else BLACK

        elif smove.startswith('position startpos'):
            params = smove.split(' ')
            #startpos
            pos = tools.parseFEN(tools.FEN_INITIAL)
            color = WHITE

            i = 0
            while i < len(params):
                param = params[i]
                if param == 'moves':
                    i += 1
                    while i < len(params):
                        mymove = params[i]
                        logging.debug(mymove)
                        m = tools.mparse(color, mymove)
                        logging.debug(m)
                        pos = pos.move(m)
                        color = 1-color
                        i += 1
                i += 1

        elif smove.startswith('go'):
            #  default options
            depth = 1000
            movetime = -1

            # parse parameters
            params = smove.split(' ')
            if len(params) == 1: continue

            i = 0
            while i < len(params):
                param = params[i]
                if param == 'depth':
                    i += 1
                    depth = int(params[i])
                if param == 'movetime':
                    i += 1
                    movetime = int(params[i])
                if param == 'wtime':
                    i += 1
                    our_time = int(params[i])
                if param == 'btime':
                    i += 1
                    opp_time = int(params[i])
                i += 1

            forced = False

            moves_remain = 40

            start = time.time()
            ponder = None
            for _ in searcher._search(pos):
                moves = tools.pv(searcher, pos, include_scores=False)

                if show_thinking:
                    entry = searcher.tp_score.get((pos, searcher.depth, True))
                    score = int(round((entry.lower + entry.upper)/2))
                    usedtime = int((time.time() - start) * 1000)
                    moves_str = moves if len(moves) < 15 else ''
                    print('info depth {} score cp {} time {} nodes {} pv {}'.format(searcher.depth, score, usedtime, searcher.nodes, moves_str))
                    logging.debug('info depth {} score cp {} time {} nodes {} pv {}'.format(searcher.depth, score, usedtime, searcher.nodes, moves_str))

                if len(moves) > 5:
                    ponder = moves[1]

                if movetime > 0 and (time.time() - start) * 1000 > movetime:
                    break

                if (time.time() - start) * 1000 > our_time/moves_remain:
                    break

                if searcher.depth >= depth:
                    break

            entry = searcher.tp_score.get((pos, searcher.depth, True))
            m, s = searcher.tp_move.get(pos), entry.lower
            # We only resign once we are mated.. That's never?
            if s == -sunfish.MATE_UPPER:
                print('resign')
                logging.debug('resign')
            else:
                moves = moves.split(' ')
                if len(moves) > 1:
                    #print('bestmove ' + moves[0] + ' ponder ' + moves[1])
                    print('bestmove ' + moves[0])
                    logging.debug('bestmove ' + moves[0])
                else:
                    print('bestmove ' + moves[0])
                    logging.debug('bestmove ' + moves[0])

        elif smove.startswith('time'):
            our_time = int(smove.split()[1])

        elif smove.startswith('otim'):
            opp_time = int(smove.split()[1])

        else:
            pass

if __name__ == '__main__':
    main()
