class Discount:
    def __init__(self):
        self.discount_factor_series = {}
        
        def calculateSvenssonInterestRate(svensson, t_delta):
            
            if (t_delta == 0):
                return 1

            if (t_delta > 30):
                t_delta = 30
            
            svensson_parameters = svensson["parameters"]

            b0,b1,b2,b3,t1,t2 = (
                svensson_parameters["b0"],
                svensson_parameters["b1"],
                svensson_parameters["b2"],
                svensson_parameters["b3"],
                svensson_parameters["t1"],
                svensson_parameters["t2"],
            )

            m1 = (1-exp(-t_delta/t1)) / (t_delta/t1)
            m2 = (1-exp(-t_delta/t2)) / (t_delta/t2)

            rate =  b0 + (b1+b2)*m1 - b2 * exp(-t_delta/t1) + b3*(m2-exp(-t_delta/t2))
           
            # Convert to coefficient, e.g. if rate=2.5%, then return 1.025
            return 1 + (rate/100)
        
        # For fixed interest rate
        if config.DISCOUNT_MODEL in (InterestRateModel.FIXED, InterestRateModel.ZERO):
            if config.DISCOUNT_MODEL == InterestRateModel.FIXED:
                # Check that the interest rate is set for fixed rate
                if (config.DISCOUNT_CONFIG[InterestRateModel.FIXED]["fixed_rate"] == None):
                    raise Exception("Fixed interest rate must be set in order to determine the discount factor")
                fixed_rate = config.DISCOUNT_CONFIG[InterestRateModel.FIXED]["fixed_rate"]
            if config.DISCOUNT_MODEL == InterestRateModel.ZERO:
                fixed_rate = 0
            for t_delta in range(0, config.TERMINAL_AGE-30+1):
                self.discount_factor_series[t_delta] = pow(1 + fixed_rate,-t_delta)         


        # For svensson interest rate
        if config.DISCOUNT_MODEL == InterestRateModel.SVENSSON:
            for t_delta in range(0, config.TERMINAL_AGE-30+1):
                self.discount_factor_series[t_delta] = pow(calculateSvenssonInterestRate(config.DISCOUNT_CONFIG[InterestRateModel.SVENSSON], t_delta) ,-t_delta)    
