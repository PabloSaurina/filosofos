from multiprocessing import Lock, Condition, Value

class Table():
    
    def __init__(self,nphil,manager):
        
        self.nphil = nphil
        self.phil =  manager.list([False]*nphil)
        self.eating = Value('i',0)
        self.actual = None
        
        self.mutex = Lock()
        self.freefork = Condition(self.mutex)
        
    def set_current_phil(self,n):
        
        self.actual = n
        
    def free_forks(self):
        
        n = self.actual
        return not(self.phil[(n+1)%self.nphil]) and not(self.phil[(n-1)%self.nphil])
    
    def wants_eat(self,n):
        
        self.mutex.acquire()
        self.freefork.wait_for(self.free_forks)
        self.phil[n] = True
        self.eating.value += 1
        self.mutex.release()
        
    def wants_think(self,n):
        
        self.mutex.acquire()
        self.phil[n] = False
        self.eating.value -= 1
        self.freefork.notify()
        self.mutex.release()


class CheatMonitor():
    
    def __init__(self):
        
        self.eating = Value('i',0)
        self.mutex = Lock()
        self.thinkingallowed = Condition(self.mutex)
        
    def is_eating(self,n):
        
        self.mutex.acquire()
        self.eating.value +=1
        self.thinkingallowed.notify()
        self.mutex.release()
    
    def all_eating(self):
        
        return self.eating.value == 2
        
    def wants_think(self,n):
        
        self.mutex.acquire()
        self.thinkingallowed.wait_for(self.all_eating)
        self.eating.value -= 1
        self.mutex.release()


class AnticheatTable():
    
    def __init__(self,nphil,manager):
        
        self.nphil = nphil
        self.phil =  manager.list([False]*nphil)
        self.eating = Value('i',0)
        self.actual = None
        self.amounteaten = manager.list([0]*nphil)
        
        self.mutex = Lock()
        self.freefork = Condition(self.mutex)
        
    def set_current_phil(self,n):
        
        self.actual = n
        
    def free_forks(self):
        
        n = self.actual
        return ((not(self.phil[(n+1)%self.nphil]) and not(self.phil[(n-1)%self.nphil])) and 
                self.amounteaten[n] <= self.amounteaten[(n+1)%self.nphil] and 
                self.amounteaten[n] <= self.amounteaten[(n-1)%self.nphil])
    
    def wants_eat(self,n):
        
        self.mutex.acquire()
        self.freefork.wait_for(self.free_forks)
        self.phil[n] = True
        self.amounteaten[n] += 1
        self.eating.value += 1
        self.mutex.release()
        
    def wants_think(self,n):
        
        self.mutex.acquire()
        self.phil[n] = False
        self.eating.value -= 1
        self.freefork.notify()
        self.mutex.release()

     

