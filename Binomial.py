import pandas as pd
import numpy as np

class BinomSRate:   #binomial lattice for the short rates (aka risk free rates)

    def __init__ (self, r, q, u, d, t):
        self.r = r              #risk free rate 
        self.q = q              #risk neutral probability
        self.u = u              #multiple of the up-move
        self.d = d              #multiple of the down-move
        self.t = t       
        
    def n_arrays(self):         #create n number of arrays, from n time periods
        t = self.t
        dataframe = [[] for rows in range(t+1)]
        return dataframe

    def calc_rates_d_only(self):    #calculating first line 
        t = self.t
        r = self.r
        d = self.d 
        output_d_only = [r]             
        for i in range(1,t+1):
            r = r*d                      #rate of r
            output_d_only.append(r)
        output_d_only = list(np.around(np.array(output_d_only), 4))   #convert this to a numpy array and round to 4 decimal places but keep it as a list
        return output_d_only

    def upward_mult(self, table):
        t = self.t
        r = self.r
        u = self.u
        d = self.d
        for i in range(1, t+1):
            table[i] = [x*u/d for x in table[i-1]]
            for n in range(i):
                table[i][n] = np.nan
    
    def ZeroCouponBond(self, table):
        t = self.t
        r = self.r
        u = self.u
        d = self.d
        q = self.q
        table[t][-1] = 100
        for rows in reversed(range(t)):
            table[rows][-1] = 100
            for columns in reversed(range(t)):
                table[rows][columns] = 1 / (1 + table[rows][columns]) * (q * table[rows+1][columns + 1] + q * table[rows][columns+1])
        return table
    
    def short_table(self):
        #creating n arrays
        short_table = self.n_arrays()
        #inserting first array for short rates
        short_table[0] = self.calc_rates_d_only()
        self.upward_mult(short_table)
        return short_table
    
    def short_binom(self, short_table):
        length_table = max(map(len, self.short_table()))            
        short_df = np.array([i + [" "] * (length_table-len(i)) for i in self.short_table()])
        short_df = pd.DataFrame(short_df.reshape(-1, time + 1)).sort_index(ascending=False)
        short_df = short_df.replace(np.nan, '', regex=True)
        return(short_df)
        
    
    def print_zcb_price(self):
        myClass = BinomSRate(rate, 0.5, upward_factor, downward_factor, time) 
        zcb_table = myClass.ZeroCouponBond(self.short_table())
        length_table = max(map(len, zcb_table))            
        zcb_df = np.array([i + [" "] * (length_table-len(i)) for i in zcb_table])
        zcb_df = pd.DataFrame(zcb_df.reshape(-1, time + 1)).sort_index(ascending=False)
        zcb_df = zcb_df.replace(np.nan, '', regex=True)
        return zcb_df
            
class BinomOption(BinomSRate):
    def __init__ (self, r, q, t, k, optType=" "):
        self.k = k
        self.optType = optType
        self.r = r
        self.q = q
        self.t = t
    
    def OptionPricing(self, short_table, zcb_table):
        k = self.k
        optType = self.optType
        r = self.r
        t = self.t
        q = self.q
        optType = self.optType
        if optType == "C":
            short_table[t][-1] = max(zcb_table[t][t] - k, 0)
            for rows in reversed(range(t)):
                short_table[rows][-1] = max(zcb_table[t][rows] - k, 0)
                for columns in reversed(range(t)):
                    short_table[rows][columns] = (1 / (1 + short_table[rows][columns])) * ((q * short_table[rows+1][columns + 1]) + (q * short_table[rows][columns+1]))
            return short_table
        if optType == "P":
            short_table[t][-1] = max(-zcb_table[t][t] + k, 0)
            for rows in reversed(range(t)):
                short_table[rows][-1] = max(-zcb_table[t][rows] + k, 0)
                for columns in reversed(range(t)):
                    short_table[rows][columns] = 1 / (1 + short_table[rows][columns]) * (q * short_table[rows+1][columns + 1] + q * short_table[rows][columns+1])
            return short_table


def initialisation():
    #initialization
    time = int(input("What is the time period (t): "))
    rate = float(input("What is the short rate? (r) (Enter in decimals): "))
    upward_factor = float(input("What is the upward factor? (u) : "))
    downward_factor = 1 / upward_factor
    user_input = int(input("What do you want to calculate?\n1. Zero Coupon Bonds: \n2. Zero Coupon Bonds Option Pricing: "))
    return time, rate, upward_factor, downward_factor, user_input

time, rate, upward_factor, downward_factor, user_input = initialisation()

# for calling methods from class and creating dataframe
myClass = BinomSRate(rate, 0.5, upward_factor, downward_factor, time) 



print("SHORT RATES BINOMIAL LATTICE")
print(myClass.short_binom(myClass.short_table()))
print("\n")


if user_input == 1:
    print("ZERO COUPON BOND BINOMIAL LATTICE")
    print(myClass.print_zcb_price())
    print("\n")

elif user_input == 2:
    #Zero coupon bond initialisation
    zcb_df = myClass.print_zcb_price()
    print("ZERO COUPON BOND BINOMIAL LATTICE")
    print(zcb_df)
    print("\n")
    
    #Option pricing initialisation
    k = int(input("What is the strike price on this Bond?: "))
    time = int(input("What is the new time period for this option?: "))
    optType = input("Is this a call option (C) or a put option (P)?: ")
    myOptClass = BinomOption(rate, 0.5, time, k, optType)

    #initialising short rates table
    optionClass = BinomSRate(rate, 0.5, upward_factor, downward_factor, time) 
    option_table = optionClass.short_table()
    print("SHORT RATES BINOMIAL LATTICE")
    print(optionClass.short_binom(optionClass.short_table()))
    print("\n")

    opt_table = myOptClass.OptionPricing(option_table, zcb_df)
    
    # print(opt_table)
    length_table = max(map(len, opt_table))            
    opt_df = np.array([i + [" "] * (length_table-len(i)) for i in opt_table])
    opt_df = pd.DataFrame(opt_df.reshape(-1, time + 1)).sort_index(ascending=False)
    opt_df = opt_df.replace(np.nan, '', regex=True)
    print("OPTION PRICING FOR ZCB BINOMIAL LATTICE")
    print(opt_df)
    print("\n")



