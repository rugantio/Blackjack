import numpy as np

class Shoe:
    '''
    The shoe is a placeholder of card decks, when shoe penetration is reached it gets reshuffled.
    '''

    def __init__(self, decks=np.uint8(6), penetration=np.float16(0.25)):
        self.decks = decks
        #available cards
        self.CARDS = np.array([2,3,4,5,6,7,8,9,10,10,10,10,11], dtype=np.uint8)
        #when to reshuffle (actual penetration)
        self.reshuffle = penetration*decks*np.uint8(13)
        #set shoe
        self.reset()
        
    def reset(self):
        '''
        set and reset
        '''
        self.cards = np.repeat(self.CARDS,self.decks)
        np.random.shuffle(self.cards)
        
    def deal(self):
        #if reshuffle penetration is reached, reset shoe
        if self.cards.size < self.reshuffle:
            self.reset()
            
        #retrieve card
        card = self.cards[0]
        #pop card from shoe
        self.cards = np.delete(self.cards,0)
        
        return card

class Hand:
    def __init__(self,cards=np.array([],dtype=np.uint8)):
        self.cards = cards
        self.value = np.uint8(0)
        
    def add_card(self,card):
        self.cards = np.append(self.cards,card)
        self.value += card
        self.evaluate()

    def evaluate(self):
        '''
        Calculates and updates the value of the hand.
        If the hand is soft and busted, calls soft_to_hard and returns hard hand
        Returns: (int) Value of the hand
        '''
        self.value = np.sum(self.cards)
        if self.is_busted():
            if np.any(self.cards == np.uint8(11)):
                self.cards = self.soft_to_hard(self.cards)
                self.value = np.sum(self.cards)
        return self.value

    @staticmethod    
    def soft_to_hard(cards):
        '''
        changes hand from soft to hard
        switch all aces value 11 with aces value 1
        '''
        return np.place(cards,cards==np.uint8(11),np.uint8(1))
    
    def is_busted(self):
        return self.value > np.uint8(21)
    
    def is_bj(self):
        return self.value == np.uint8(21) and self.cards.size == np.uint8(2)
            
class Dealer:
    def __init__(self):
        self.hand = Hand()
        
    def play(self,shoe):
        self.reset()
        while self.hand.value < np.uint(17):
            self.hit(shoe)

    def reset(self):
        self.hand = Hand()
        
    def hit(self, shoe):
        card = shoe.deal()
        self.hand.add_card(card)
        bj = self.exp_val(shoe)
        extra = 'Stand' if self.hand.value > np.uint8(16) else 'Hit'
        if self.hand.is_bj():
            extra = 'BJ!' 
        if self.hand.is_busted():
            extra = 'Busted!'
        print(self.hand.cards,self.hand.value,extra,bj)
    
    def exp_val(self,shoe):
        '''
        expected value 
        '''
        #stub for BJ
        if self.hand.cards.size == np.uint8(1):
            if np.any(self.hand.value + shoe.CARDS == np.uint8(21)):
                return('BJ prob: {}'.format(np.uint8(100)*np.sum(self.hand.value + shoe.CARDS == np.uint8(21))/np.uint8(13)))    

class Player:
    pass

class Game:
    def __init__(self):
        self.shoe = Shoe()
        self.dealer = Dealer()
    
    def play(self):
        self.dealer.play(self.shoe)
        
if __name__ == "__main__":
    '''
    ONLY SIMULATE DEALER PLAYING BY HIMSELF 
    '''
    a = Game()
    for i in range(5):
        a.play()
        print('END')
