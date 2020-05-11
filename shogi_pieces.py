class Pieces:
    def __init__(self,position,team):
        self.position = position
        self.graphic = "-"
        self.promotedGraphic = "-"
        self.team = team
        self.isPromoted = False
        self.set_graphic()
    name = "Template"
    def __repr__(self):
        return self.name()
    def __str__(self):
        return self.name()
    def moves(self):
        print("Default class has no moves")
    def promotion_row(self):
        if self.team == 'white': return [(0,4),(1,4),(2,4),(3,4),(4,4)]
        elif self.team == 'black': return [(0,0),(1,0),(2,0),(3,0),(4,0)]
    def set_graphic(self):
        self.graphic = "-"
    def move_limits(self,directions,occupied_positions):
        ranging_moves = []
        for direction in directions:
            direction_iterations = direction
            current_pos = tuple(map(lambda a,b:a+b,self.position,direction))
            while current_pos[0] >= 0 and current_pos[0] < 5 and current_pos[1] >= 0 and current_pos[1] <5:
                if current_pos not in occupied_positions:                                                       
                    ranging_moves.append(direction_iterations)
                    direction_iterations = tuple(map(lambda a,b:a+b,direction_iterations,direction))
                elif current_pos in occupied_positions:
                    ranging_moves.append(direction_iterations)
                    break
                current_pos = tuple(map(lambda a,b:a+b,current_pos,direction))
        return ranging_moves


class King(Pieces):
    def name(self):
        return "King"
    def set_graphic(self):
        if self.team =="white": self.graphic = "k"
        elif self.team =="black": self.graphic ="K"
    def moves(self,game):
        return [(0,1),(1,1),(1,-1),(-1,0),(1,0),(-1,-1),(-1,1),(0,-1)]
class Fu(Pieces):
    def name(self):
        return "Fuhyou" if not self.isPromoted else "Tokin"
    def set_graphic(self):
        if self.team =="white": 
            self.graphic = "f"
            self.promotedGraphic = "t"
        elif self.team =="black": 
            self.graphic ="F"
            self.promotedGraphic = "T"
    def moves(self,game):
        if self.team == "white": 
            return [(0,1)] if not self.isPromoted else [(0,1),(-1,1),(1,1),(-1,0),(1,0),(0,-1)]
        if self.team == "black": 
            return [(0,-1)] if not self.isPromoted else [(0,-1),(-1,-1),(1,-1),(-1,0),(1,0),(0,1)]
class Gold(Pieces):
    def name(self):
        return "Gold"
    def set_graphic(self):
        if self.team =="white": self.graphic = "g"
        elif self.team =="black": self.graphic ="G"
    def moves(self,game):
        if self.team == "white": return [(0,1),(-1,1),(1,1),(-1,0),(1,0),(0,-1)]
        elif self.team == "black": return [(0,-1),(-1,-1),(1,-1),(-1,0),(1,0),(0,1)]
class Silver(Pieces):
    def name(self):
        return "Silver" if not self.isPromoted else "Narikin"
    def set_graphic(self):
        if self.team =="white": 
            self.graphic = "s"
            self.promotedGraphic = "n"
        elif self.team =="black": 
            self.graphic ="S"
            self.promotedGraphic = "N"
    def moves(self,game):
        if self.team == "white": 
            return [(1,1),(-1,-1),(-1,1),(1,-1),(0,1)] if not self.isPromoted else [(0,1),(-1,1),(1,1),(-1,0),(1,0),(0,-1)]
        elif self.team == "black": 
            return [(1,1),(-1,-1),(-1,1),(1,-1),(0,-1)] if not self.isPromoted else [(0,-1),(-1,-1),(1,-1),(-1,0),(1,0),(0,1)]
class Bishop(Pieces):
    def name(self):
        return "Bishop" if not self.isPromoted else "Dragon Horse"
    def set_graphic(self):
        if self.team =="white": 
            self.graphic = "b"
            self.promotedGraphic = "h"
        elif self.team =="black": 
            self.graphic ="B"
            self.promotedGraphic = "H"
    def moves(self,occupied_pos):
        return self.move_limits([(-1,-1),(-1,1),(1,-1),(1,1)],occupied_pos) if not self.isPromoted else self.move_limits([(-1,-1),(-1,1),(1,-1),(1,1)],occupied_pos) + [(1,0),(0,1),(-1,0),(0,-1)]
class Rook(Pieces):
    def name(self):
        return "Rook" if not self.isPromoted else "Dragon"
    def set_graphic(self):
        if self.team =="white": 
            self.graphic = "r"
            self.promotedGraphic = "d"
        elif self.team =="black": 
            self.graphic ="R"
            self.promotedGraphic = "D"
    def moves(self,game):
        return self.move_limits([(1,0),(0,1),(-1,0),(0,-1)],game) if not self.isPromoted else self.move_limits([(1,0),(0,1),(-1,0),(0,-1)],game) + [(-1,-1),(-1,1),(1,-1),(1,1)]


