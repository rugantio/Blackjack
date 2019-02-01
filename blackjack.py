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
        self.busted = 0
        
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

        #check for double aces
        if np.array_equal(self.cards,np.array([11,11],dtype=np.uint8)):
            self.cards = np.array([11,1],dtype=np.uint8)
            self.value = np.uint(12)
            return self.value

        #if hand is busted 
        if self.value > np.uint8(21):
            #check for soft ace and change it to hard
            if np.any(self.cards == np.uint8(11)):
                self.soft_to_hard()
                self.value = np.sum(self.cards)
                return self.value
            #hand is really busted
            else:
                self.busted = 1
                return self.value
       
    def soft_to_hard(self):
        '''
        changes hand from soft to hard
        switch all aces value 11 with aces value 1
        returns: nothing, the modification is done in place!
        '''
        np.place(self.cards,self.cards==np.uint8(11),np.uint8(1))
    
    def is_busted(self):
        '''
        Check if hand is busted
        returns: (boolean)
        '''
        self.evaluate()
        return self.value > np.uint8(21)
    
    def is_bj(self):
        '''
        Check if hand is blackjack
        returns: (boolean)
        '''
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
        
        action = 'Stand' if self.hand.value > np.uint8(16) else 'Hit'
        if self.hand.is_bj():
            action = 'BJ!' 
        if self.hand.is_busted():
            action = 'Busted!'
        print(self.hand.cards,self.hand.value,action)
        
    def exp_val(self,shoe):
        '''
        Calculates probabilistic expected final hand values for the dealer.
        The dealer stands on soft 17.
        Given the initial card, we can expand the tree of available future 
        states.
        The final probability for hand value >= is found as the ratio:
        #favorable states/#all possible states, but the transition from one state
        into another is probabilistic, it doesn't take into account cards that have 
        come out from shoe before this hand (shoe history) and the shoe penetration.
        A minor adjustment is made to take into account cards that have come out
        in this hand. 
        
        '''
        # [p_17,p_18,p_19,p_20,p_21,p_bust]
        exp = np.array([0,0,0,0,0,0],dtype=np.float16)
        # tot = 13 x 4 x decks
        tot_cards = np.uint16(52)*shoe.decks
        
        #factor to multiply occurrences = 4 x decks x ...
        factor = np.uint16(4)*shoe.decks
        
        #possible values to be drawn
        next_values = shoe.CARDS + self.hand.value
        
        #parse for bj
        if np.array_equal(self.hand.cards,np.array([11],dtype=np.uint8)) or\
        np.array_equal(self.hand.cards,np.array([10],dtype=np.uint8)): 
            #bj_prob         
            p_bj = (np.sum(next_values == np.uint8(21))*factor)/(tot_cards - np.uint8(1))
        else:
            p_bj = 0
                   
        def git(next_values,cycle=1):
            '''
            recursive function to get probs
            '''       
            move = (1/13)**(cycle - 1)
            print('calling git on {}'.format(next_values))
            print('DEPTH = {}, move = {}'.format(cycle,move))


            for i in reversed(sorted(np.unique(next_values))):
                #cards that have come out in this hand are less likely to come 
#                if i - self.hand.value == self.hand.value:
#                    factor -= 1
              
                #I order (one transition) exp values                                                             h
                if i >= 17:
#                    exp[i-17] += (np.sum(i == next_values)*factor)/(tot_cards - np.uint8(1))
                    print('i = {}, before exp={}'.format(i, 100*exp))
                    if i > 21:
                        exp[5] += (np.sum(i > 21)*factor*move)/(tot_cards - np.uint8(cycle))
                    else:
                        exp[i-17] += (np.sum(i == next_values)*factor*move)/(tot_cards - np.uint8(cycle))
                    print('i = {}, after exp={}'.format(i, 100*exp))

                ## II order
                else:
                    new_next = i + shoe.CARDS
                    #if hand is busted change all aces to soft
                    if i + 11 > 21:
                        np.place(new_next,new_next==(i+11),np.uint8(i+1))
                    print('LEAF = {}, calling git on {}'.format(i, new_next))
                    git(new_next,cycle=cycle+1)
            return 100*exp
        return git(next_values)
    
#    
#                #put discount factor back in
#                if i - self.hand.value == self.hand.value:
#                    factor += 1

#TODO:
# handle double ace: at the beginning is still 22
# go to higher orders recursively
# discount factor for cards already drawn (only working at the first turn)

class Player:
    pass

class Game:
    def __init__(self):
        self.shoe = Shoe()
        self.dealer = Dealer()
    
    def play(self):
        self.dealer.play(self.shoe)        
        
if __name__ == "__main__":
    a = Dealer(); s = Shoe(); a.hit(s); a.exp_val(s)

#if __name__ == "__main__":
#    '''
#    ONLY SIMULATE DEALER PLAYING BY HIMSELF 
#    '''
#    a = Dealer(); s = Shoe(); a.hit(s); a.exp_val(s)
#    for i in range(5):
#        a = Game()
#        a.play()
#        print('END\n')
