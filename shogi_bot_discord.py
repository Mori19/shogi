import discord
from discord.ext import commands
import re
import shogibot_token
import shogi_pieces
import pickle


class Player:
    def __init__(self,who,hand,team,id):
        self.who = who
        self.id = id
        self.hand = hand
        self.team = team
        self.threat = False
    def __repr__(self):
        return "A player of a game of shogi"
    def __str__(self):
        return "A player of a game of shogi"      

class Game:
    def __init__(self,mode):
        self.mode = mode
        self.size = self.board_size(mode)
        self.playing = 1
        self.setup(self.mode)
        self.occupy_positions()
        self.persistent_board = False
        
    def __repr__(self):
        return "A game of Shogi"
    def __str__(self):
        return "A game of Shogi"
        
    def board_size(self,mode):
        sizes = {'mini':5,'standard':9}
        return sizes[mode]
    
    def setup(self,mode): 
        mode_map = {'mini':list(zip([i for i in range(-1,-6,-1)],
                                    [4 for i in range(0,5)]))+[(-5,3)]
                    +list(zip([i for i in range(-5,0,1)],
                              [0 for i in range(0,5)]))+[(-1,1)],
                   'standard':list(zip([i for i in range(-1,-10,-1)]
                                       ,[8 for i in range(0,10)]))
                   +[(-8,7),(-2,7)]+list(zip([i for i in range(-1,-10,-1)],
                                             [6 for i in range(0,10)]))
                   +list(zip([i for i in range(-9,0,1)]
                                       ,[0 for i in range(0,10)]))
                   +[(-2,1),(-8,1)]+list(zip([i for i in range(-1,-10,-1)],
                                             [2 for i in range(0,10)]))}
        self.turn = 'black'
        self.player1 = Player('vacant',[],'black','')
        self.player2 = Player('vacant',[],'white','')
        self.player_list = [self.player1,self.player2]
        self.playermap = {'black':self.player1,'white':self.player2}

        self.piece_list = {}
        mode_map_pieces = {'mini':[shogi_pieces.Rook,
                          shogi_pieces.Bishop,
                          shogi_pieces.Silver,
                          shogi_pieces.Gold,
                          shogi_pieces.King,
                          shogi_pieces.Fu,
                          shogi_pieces.Rook,
                          shogi_pieces.Bishop,
                          shogi_pieces.Silver,
                          shogi_pieces.Gold,
                          shogi_pieces.King,
                          shogi_pieces.Fu],
                           'standard':[shogi_pieces.Lance,
                                      shogi_pieces.Knight,
                                      shogi_pieces.Silver,
                                      shogi_pieces.Gold,
                                      shogi_pieces.King,
                                      shogi_pieces.Gold,
                                      shogi_pieces.Silver,
                                      shogi_pieces.Knight,
                                      shogi_pieces.Lance,
                                      shogi_pieces.Bishop,
                                      shogi_pieces.Rook,
                                      shogi_pieces.Fu,
                                      shogi_pieces.Fu,
                                      shogi_pieces.Fu,
                                      shogi_pieces.Fu,
                                      shogi_pieces.Fu,
                                      shogi_pieces.Fu,
                                      shogi_pieces.Fu,
                                      shogi_pieces.Fu,
                                      shogi_pieces.Fu,
                                      shogi_pieces.Lance,
                                      shogi_pieces.Knight,
                                      shogi_pieces.Silver,
                                      shogi_pieces.Gold,
                                      shogi_pieces.King,
                                      shogi_pieces.Gold,
                                      shogi_pieces.Silver,
                                      shogi_pieces.Knight,
                                      shogi_pieces.Lance,
                                      shogi_pieces.Bishop,
                                      shogi_pieces.Rook,
                                      shogi_pieces.Fu,
                                      shogi_pieces.Fu,
                                      shogi_pieces.Fu,
                                      shogi_pieces.Fu,
                                      shogi_pieces.Fu,
                                      shogi_pieces.Fu,
                                      shogi_pieces.Fu,
                                      shogi_pieces.Fu,
                                      shogi_pieces.Fu
                                      ]}
        colour = {'mini':['black' for i in range(6)] + ['white' for i in range(6)],
                  'standard':['black' for i in range(20)] + ['white' for i in range(20)]}
        for piece in range(len(mode_map_pieces[mode])):
            name = "bit"+str(piece)
            self.piece_list[name] = mode_map_pieces[mode][piece](mode_map[mode][piece],colour[mode][piece])

    def occupy_positions(self):
        self.occupied_positions = []
        for piece in self.piece_list.values():
            self.occupied_positions.append(piece.position)

    def draw_board(self):
        board = [['' for i in range(0,self.size)] for i in range(0,self.size)]
        to_send = []
        to_send.append(f"The turn is: {self.turn}\nWhite hand: {str(list(map(lambda a:a.graphic,self.player2.hand)))}\n")
        to_send.append(('` '+'{:^4}'*self.size+'`\n').format(*(range(self.size,0,-1))))
        for piece in self.piece_list.values():
            if piece.position != (-1,-1): 
                print(piece.position)
                board[piece.position[1]][piece.position[0]] = piece.graphic
        for number, row in enumerate(board,1):
            to_send.append(('`|'+'{:_^3}|'*self.size+'{:^3}`').format(*row,str(number)))
            to_send.append("\n")
        to_send.append("Black hand: {}\n".format(str(list(
            map(lambda a:a.graphic,self.player1.hand)))))
        return ''.join(to_send)



    def change_turn(self):
        if self.turn == 'black':
            self.turn = 'white'
        elif self.turn == 'white':
            self.turn = 'black'

    def promote(self,piece,last_pos = (3,3)):
        if (piece.position not in piece.promotion_row(self.size))\
        and (last_pos not in piece.promotion_row(self.size)):
            return "you are not in a promotion row\n"
        piece.isPromoted = True
        piece.graphic = piece.promotedGraphic
        return "Promoted!\n"

    def check_rules(self,piece,position,new_position):
        if tuple(map(lambda a,b:a-b,new_position, position))\
        in piece.moves(self.occupied_positions,self.size)\
        and False not in tuple(map(lambda a : abs(a)>=0, 
                                   list(map(lambda a,b : b-a, new_position, (self.size,self.size))))):
            for other_piece in self.piece_list.values():
                if other_piece.position == new_position\
                and other_piece.team == piece.team\
                and other_piece != piece:
                    print("moving onto self")
                    return "A piece on your team is already there"
            return self.hypothesis_move_and_check_for_check(piece,new_position)
        else:
            print("illegal move")
            return "Illegal move; it could be out of bounds\
                    or not in the piece movelist"

    def hypothesis_move_and_check_for_check(self,piece,new_position):
        save_state = {}
        for save_piece in self.piece_list.values():
            save_state[save_piece] = [save_piece.position,
                                      save_piece.team,
                                      save_piece.isPromoted]
        save_hand = [self.player1.hand.copy(),
                     self.player2.hand.copy()]
        piece.position = new_position
        print(self.check_take_piece(piece))
        self.check_for_threat()
        if piece.team == "black" and self.player1.threat\
        or piece.team == "white" and self.player2.threat: 
            self.restore_save(save_state,save_hand)
            print("restore save - bad move")
            return "You can't check yourself!"
        print("restore save - can move")
        self.restore_save(save_state,save_hand)
        self.check_for_threat()
        return False
    
    def restore_save(self,save_state,saved_hand):
        for piece in self.piece_list.values():
            piece.position = save_state[piece][0]
            piece.team = save_state[piece][1]
            piece.isPromoted = save_state[piece][2]
        self.player_list[0].hand = saved_hand[0].copy()
        self.player_list[1].hand = saved_hand[1].copy()

    def check_take_piece(self,piece): 
        to_send = ""
        for other_piece in self.piece_list.values():
            if other_piece.position == piece.position:
                if other_piece != piece:
                    to_send+="Piece taken!\n"
                    other_piece.position = (-1,-1)
                    other_piece.team = piece.team
                    other_piece.isPromtoed = False
                    other_piece.set_graphic()
                    for player in self.player_list:
                        if player.team == other_piece.team:
                            player.hand.append(other_piece)
        return to_send



    def drop_piece(self,move,active_piece):
        shuffle = range(self.size,0,-1)
        horizontal = -int(move[2])
        vertical = int(move[3])-1
        for piece in self.piece_list.values():
            if piece.position == (horizontal,vertical):
                return "You cannot drop onto another piece.\n"
        if type(active_piece) == shogi_pieces.Fu:
            if (horizontal,vertical) in active_piece.promotion_row(self.size):
                return "You cannot drop {} in the promotion row".format(str(active_piece))
            for piece in self.piece_list.values():
                if type(piece) == shogi_pieces.Fu and\
                piece.position[0] == horizontal\
                and not active_piece.isPromoted\
                and active_piece.team == self.turn:
                    return "You cannot stack this piece (only one per column)"
        active_piece.position = (horizontal,vertical)
        return "dropped"




    def enact_move(self, piece,new_pos):
        if not self.check_rules(piece,piece.position,new_pos):
            piece.position = new_pos
            return False
        else:
            return self.check_rules(piece,piece.position,new_pos)
        
    def autopromotion_protocol(self,piece):
        if not piece.isPromoted and piece.position in piece.promotion_row(self.size): 
            return self.promote(piece)

    def get_piece(self,move,horizontal,vertical):
        if len(move) == 3 or len(move) == 4:
            for piece in self.piece_list.values():
                if piece.graphic == move[0]:
                    if tuple(map(lambda a,b:a-b,
                                 (horizontal,vertical),
                                 piece.position))\
                    in piece.moves(self.occupied_positions,self.size):
                        return piece
        elif len(move) == 5 or len(move) == 6:
            shuffle = range(self.size,0,-1)
            current_x = int(move[1])-1
            current_y = int(move[2])-1
            for piece in self.piece_list.values():
                if piece.position == (shuffle[current_x],current_y):
                    return piece

    def check_for_threat(self):
        self.player1.threat = False
        self.player2.threat = False
        for piece in self.piece_list.values():
            if type(piece) == shogi_pieces.King and piece.team == 'white':
                white_king = piece
            elif type(piece) == shogi_pieces.King and piece.team == 'black':
                black_king = piece
        for piece in self.piece_list.values():
            for move in piece.moves(self.occupied_positions,self.size):
                if piece.team == "black"\
                and white_king.position == tuple(map(lambda a,b:a+b,
                                                          piece.position,move)):
                    self.player2.threat = True
                elif piece.team == "white"\
                and black_king.position == tuple(map(lambda a,b:a+b,
                                                          piece.position,move)):
                    self.player1.threat = True
                    
    def warn_check(self):
        to_send = ""
        if self.player1.threat: to_send+="Black is in check!"
        if self.player2.threat: to_send+="White is in check!"
        return to_send





    def computer_moves():
        #randomly select a piece, 
        #randomly select a legal move, 
        #and format a string that we can work with
        my_pieces = []
        for piece in piece_list.values(): #get what pieces we can work with
            if piece.team == 'white':
                my_pieces.append(piece)
        my_active_piece = my_pieces[random.randint(0,len(my_pieces))]
          
def check_for_checkmate(ctx,game):
    save_state = pickle.dumps(game)
    print(f'the game turn is {game.turn}')
    for piece in game.piece_list.values():
        if piece.team == game.turn and piece.position != (-1,-1):
            print(f'the now piece is {piece.team}')
            print(piece)
            for move in piece.moves(game.occupied_positions,game.size):
                print(f'the move to check is {move}')
                if not game.enact_move(piece,tuple(map(lambda a,b:a+b,
                                                       piece.position,
                                                       move))):
                    games[ctx.channel.id] = pickle.loads(save_state)
                    print("pickle loaded")
                    return False
    game = pickle.loads(save_state)
    return "Thats checkmate!"

class Person:
    def __init__(self,id,name):
        self.id = id
        self.name = name
        self.wins = 0
        self.loss = 0
        
def update_scoreboard(ctx):
    if games[ctx.channel.id].player1.id not in people.keys():
        people[games[ctx.channel.id].player1.id] = Person(games[ctx.channel.id].player1.id,
                                                          games[ctx.channel.id].player1.who)
    if games[ctx.channel.id].player2.id not in people.keys():
        people[games[ctx.channel.id].player2.id] = Person(games[ctx.channel.id].player2.id,
                                                          games[ctx.channel.id].player2.who)
    if games[ctx.channel.id].turn == "black":
        people[games[ctx.channel.id].player1.id].loss +=1
        people[games[ctx.channel.id].player2.id].wins +=1
    else:
        people[games[ctx.channel.id].player1.id].wins +=1
        people[games[ctx.channel.id].player2.id].loss +=1
    with open('save_scoreboard.pickle','wb') as save_file:
        pickle.dump(people,save_file)
        
people = {}
bot = commands.Bot(command_prefix='!',
                   description="A bot to play shogi with on discord.\
                   Currently lets you play minishogi.")
games = {}

@bot.event
async def on_ready():
    global people
    print(f'{bot.user.name} has connected to Discord!')
    await bot.change_presence(activity=discord.Game(name="Shogi"))
    try:
        with open('save_scoreboard.pickle','rb') as save_file:
            people = pickle.load(save_file)
    except:
        print("No saved scoreboard file found!")
    #status=discord.Status.idle

@bot.command(name='new-game',help='make a game')
async def initialise(ctx,mode = 'mini'):
    if mode not in ['mini','standard']:
        await ctx.send("Game mode unavailable!")
        return False
    games[ctx.channel.id] = Game(mode)
    await ctx.send(games[ctx.channel.id].draw_board())
    
def turn_end(ctx,game):
    to_say = []
    if game.persistent_board: to_say.append(game.draw_board())
    game.check_for_threat()
    if game.warn_check(): 
        to_say.append(game.warn_check())
        message = check_for_checkmate(ctx,game)
        if message: 
            to_send.append(message)
            update_scoreboard(ctx)
            game.playing = False
    return '\n'.join(to_say)

@bot.command(name='move',help='follow this command with a move')
async def make_move(ctx,move):
    try:
        if not games[ctx.channel.id].playing:
            await ctx.send("The game is over")
            return False
    except:
        await ctx.send("No current game")
        return False
    print(games)
    if ctx.author.id != games[ctx.channel.id].player1.id\
    and ctx.author.id != games[ctx.channel.id].player2.id:
        await ctx.send("You are not a player in the game!")
        return None
    games[ctx.channel.id].check_for_threat()
    games[ctx.channel.id].occupy_positions()
    if re.search("^[fkgsbrFKGSBRnNtTdDhH](\d\d|\d\d\d\d)p?$",move):
        shuffle = range(games[ctx.channel.id].size,0,-1)
        if len(move) <= 4:
            horizontal = -int(move[1])
            vertical = int(move[2])-1
        elif len(move) >= 5:
            horizontal = -int(move[3])
            vertical = int(move[4])-1        
        active_piece = games[ctx.channel.id].get_piece(move,
                                                       horizontal,
                                                       vertical)
        if active_piece:
            if games[ctx.channel.id].playermap[games[ctx.channel.id].turn].id != ctx.author.id:
                await ctx.send("It isn't your turn!")
                return None
            last_pos = active_piece.position #so we can promote
                                             # when we leave the row, not just enter it
            if active_piece.team == games[ctx.channel.id].turn: 
                if not games[ctx.channel.id].enact_move(active_piece,
                                                        (horizontal,vertical)): 
                    message = games[ctx.channel.id].check_take_piece(active_piece)
                    if message: await ctx.send(message)
                    if move[-1] == 'p' or move[-1] == '+': await ctx.send(
                        games[ctx.channel.id].promote(active_piece,last_pos))
                    games[ctx.channel.id].change_turn()
                else: await ctx.send(games[ctx.channel.id].enact_move(
                    active_piece, (horizontal,vertical)))
            else:
                await ctx.send("That piece does not\
                               match the current turn!")
        else:
            await ctx.send("Illegal move; no valid path\n")
        if type(active_piece) == shogi_pieces.Fu: 
            message = games[ctx.channel.id].autopromotion_protocol(active_piece)
            if message: await ctx.send(message)
    #cut drop from here
    message = turn_end(ctx,games[ctx.channel.id])
    if message: await ctx.send(message)

    
@bot.command(name='drop',help='drop a piece on the board')
async def drop(ctx,move):
    try:
        if games[ctx.channel.id].playermap[games[ctx.channel.id].turn].id != ctx.author.id:
            await ctx.send("It isn't your turn!")
            return None
    except:
        await ctx.send("There is no active game")
    if not re.search("[fgsrbFSGRB]\d\d",move): 
        await ctx.send("Drop moves should be made in format pXY")
    dropped = False
    for piece in games[ctx.channel.id].playermap[games[ctx.channel.id].turn].hand:
        if move[0] == piece.graphic:
            message = games[ctx.channel.id].drop_piece(move,piece)
            if message == "dropped":
                games[ctx.channel.id].playermap[games[ctx.channel.id].turn].hand.remove(piece)
                dropped = True
                games[ctx.channel.id].change_turn()
                break
            else:
                await ctx.send(message)
    if not dropped: await ctx.send("You do not have a piece to drop/made an illegal drop")
    message = turn_end(ctx,games[ctx.channel.id])
    if message: await ctx.send(message)
    
@bot.command(name='show-board',help='show the board')
async def draw_table(ctx):
    try:
        await ctx.send(games[ctx.channel.id].draw_board())
    except:
        await ctx.send("No active game")
        
@bot.command(name='persistent-board',help='Whether to print the board every move or not')
async def persistent_board(ctx):
    try:
        games[ctx.channel.id].persistent_board = True if not games[ctx.channel.id].persistent_board else False
    except:
        await ctx.send("No active game")
@bot.command(name='players',help='show players in the current game')
async def show_players(ctx):
    try:
        await ctx.send(f"Black is: {+games[ctx.channel.id].player1.who}\
                       \nWhite is: {games[ctx.channel.id].player2.who}")
    except:
        await ctx.send("No active game")
@bot.command(name='register',help='Make you a player in the game')
async def register_player(ctx):
    try:
        if ctx.guild == None: games[ctx.channel.id].player2.who = 'computer'
        for player in games[ctx.channel.id].player_list:
            if player.who == 'vacant':
                player.who = ctx.author.display_name
                player.id = ctx.author.id
                await ctx.send(f"Registered as {player.team} player!")
                return
        await ctx.send("The game is full")
    except:
        await ctx.send("No active game")
    
@bot.command(name='restore',help="this function is not yet implemented")
async def restore_game(ctx):
    await ctx.send("empty function")
@bot.command(name='scoreboard',help="show the current leaderboard")
async def show_scores(ctx):
    to_send = "`SCOREBOARD:\n"
    to_send += "{:<11}{:<5}{:<5}\n".format("Player","Wins","Loss")
    for person in people.values():
        to_send += '{:<11} {:>5} {:>5}\n'.format(person.name,person.wins,person.loss)
    to_send+='`'
    await ctx.send(to_send)
    
@bot.command(name='resign',help='forfeit the current game')
async def forfeit_game(ctx):
    if games[ctx.channel.id].playermap[games[ctx.channel.id].turn].id != ctx.author.id:
        await ctx.send("You have resigned!")
        update_scoreboard(ctx)
    else:
        await ctx.send("It isn't your turn")

@bot.command(name='rules',help='display the rules')
async def get_help(ctx):
    await ctx.send("Moves are made in format piece, horizontal and then vertical\
    (you can also specify where from if needed). eg white silver to column 3 row\
    2 would be s32.\nYou cannot drop a pawn in the same row as another pawn, nor\
    can you drop it in the promotion row. The final row is the promotion row, and\
    you can promote moving in or out.\nk - 王\ng - 金\ns - 銀  n - 成金\nb - 角  h\
    ‐ 竜馬\nr - 車  d ‐ 竜王\nf ‐ 歩  t ‐ と金")
    
@bot.command(name="ルール")
async def help_wrapper(ctx):
    await get_help(ctx)

#@bot.command(name='表示')
#await draw_table(ctx)
bot.run(shogibot_token.TOKEN)





