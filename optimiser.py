from random import randint, random
from math import exp, log
from WarehouseSHAD import Warehouse
def dist(p1: tuple, p2: tuple) -> float:
    warehouse_instance = Warehouse()
    return warehouse_instance.distance(p1[0], p1[1], p2[0], p2[1])

def lenght(path: list[tuple]) -> float:
    result = 0.0
    for i in range(len(path) - 1):
        result += dist(path[i], path[i + 1])
    return result

t0 = 1.0

class Otjig:
    def cool(self, step: int):
        self.temp = t0*0.99**step

    def otjig(self):
        swap1 = randint(1, len(self.cur) - 1)
        swap2 = randint(1, len(self.cur) - 1)
        new = self.cur.copy()
        new[swap1], new[swap2] = new[swap2], new[swap1]
        new_res = lenght(new)
        
        if new_res < self.cur_result or random() < exp((self.cur_result - new_res) / self.temp):
            self.cur_result = new_res
            self.cur = new

    def optimise(self, inp: list[tuple], start_point, iterations=1000) -> list[tuple]:
        self.cur = inp.copy()
        self.cur_result = lenght(self.cur)
        for i in range(iterations):
            self.cool(i + 1)
            self.otjig()
        result = self.cur.copy()
        result = [start_point] + result + [start_point]
        result_fin=[]
        hor_lines=[2,19,38,42,64,82]
        for i in range(0,len(result)):
            if i == len(result) - 1:
                result_fin.append(result[i])
            else:
                x = result[i][0]
                y = result[i][1]
                xn = result[i + 1][0]
                yn = result[i + 1][1]
                result_fin.append(result[i])
                if (x == xn or x + 2 == xn) and x%3==1:
                    x+=1
                    result_fin.append((x,y))
                    while y > yn:
                        y -=1
                        result_fin.append((x,y))
                    while y< yn:
                        y+=1
                        result_fin.append((x,y))
                else:
                    if (x==xn or xn+2==x) and x%3==0:
                        x -= 1
                        result_fin.append((x,y))
                        while y > yn:
                            y -= 1
                            result_fin.append((x,y))
                        while y < yn:
                            y += 1
                            result_fin.append((x,y))
                    else:
                        hor_line=hor_lines[0]
                        for i in hor_lines:
                            if (max(i,y) - min(i,y) + max(i,yn) - min(yn,i)) < (max(hor_line,y) - min(hor_line,y) + max(hor_line,yn) - min(yn,hor_line)):
                                hor_line=i
                        if hor_line > y:
                            while y < hor_line:
                                y+=1
                                result_fin.append((x,y))
                        else:
                            while y > hor_line:
                                y-=1
                                result_fin.append((x,y))
                        if xn%3 == 1:
                            if x > xn:
                                while x != xn+1:
                                    x-=1
                                    result_fin.append((x,y))
                            else:
                                while x!=xn+1:
                                    x+=1
                                    result_fin.append((x,y))
                            if y > yn:
                                while y!=yn:
                                    y-=1
                                    result_fin.append((x,y))
                            if y < yn:
                                while y!=yn:
                                    y+=1
                                    result_fin.append((x,y))
                        else:
                            if x > xn:
                                while x != xn-1:
                                    x-=1
                                    result_fin.append((x,y))
                            else:
                                while x!=xn-1:
                                    x+=1
                                    result_fin.append((x,y))
        return result_fin
