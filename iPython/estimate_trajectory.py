import array

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
import numpy as np
import scipy.constants
from Geocentric import Geocentric
from scipy.interpolate import interp1d

geoC = Geocentric(6378137, 6356752.314)
f0 = 143050000
c = scipy.constants.c
trans_station_point = np.array(geoC.GeographicToGeocentric(47.347993, 5.515079, 190))

def make_meteor():
    ## initial meteor trajectory guess 
    est_start_altitude = np.random.normal(100e3,20e3,1)
    est_stop_altitude = np.random.normal(60e3,20e3,1)
    
    est_start_lat = np.random.normal(49,1,1)  
    est_start_lon = np.random.normal(11,1,1)
    
    est_stop_lat = np.random.normal(49,1,1) 
    est_stop_lon = np.random.normal(11,1,1)
    
    est_velocity = np.random.normal(50000,20000,1)

    est_start_point = np.array(geoC.GeographicToGeocentric(est_start_lat, est_start_lon, est_start_altitude))
    est_stop_point = np.array(geoC.GeographicToGeocentric(est_stop_lat, est_stop_lon, est_stop_altitude))
    est_vect = est_start_point - est_stop_point
    est_speed_vect = est_vect/np.linalg.norm(est_vect) * est_velocity
    est_params = np.concatenate((est_start_point.ravel(), est_speed_vect.ravel()), axis=1)
    return est_params


def make_deap_meteor():
    return array.array('d',make_meteor())

def estimate_dopplers(trajectory, timesteps, f0, trans_station, rec_station):
    '''
        Returns array of dopplers for given transmitter to receiver position and defined frequency and known trajectory.
    '''
    rec_to_met = np.empty([trajectory.shape[0], 1])
    trans_to_met = np.empty([trajectory.shape[0], 1])
    doppler = np.empty([trajectory.shape[0], 2])
    
    previous_rec_to_met = np.linalg.norm(rec_station - trajectory[0])
    previous_trans_to_met = np.linalg.norm(trans_station - trajectory[0])
    
    t = timesteps[1] - timesteps[0]
    
    for i in range(trajectory.shape[0]):
        rec_to_met[i] = np.linalg.norm(rec_station - trajectory[i])
        trans_to_met[i] = np.linalg.norm(trans_station - trajectory[i])
    
        met_trans_speed = previous_trans_to_met - trans_to_met[i]
        previous_trans_to_met = trans_to_met[i]
        speed = met_trans_speed/t    
        f1 = ((c + speed)/c * f0)
        
        met_rec_speed = previous_rec_to_met - rec_to_met[i]    ## calculate bistatic velocity from known position
        previous_rec_to_met = rec_to_met[i]
        speed = met_rec_speed/t
        f2 = (c/(c - speed) * f1)
        doppler[i] = np.array([timesteps[i], f2-f0])
    return doppler

def error_func(est_params, timesteps, stations):
    """
    Returns difference between real and estimated meteor trajectory dopplers
    """
    from Geocentric import Geocentric
    geoC = Geocentric(6378137, 6356752.314)
    
    est_start_point = est_params[0:3]
    est_vect = est_params[3:6]
    est_points = np.empty([timesteps.size, 3])
    
    for i in range(timesteps.size):  # generate points of estimated meteor trajectory
        est_points[i] =  est_start_point + (est_vect * timesteps[i])

    doppler_deviations = {}
    for station in stations:
        doppler_deviation = np.zeros_like(station['doppler'])
        rec_station_point = np.array(geoC.GeographicToGeocentric(station['latitude'], station['longitude'], station['elevation']))
        est_doppler = estimate_dopplers(est_points, timesteps, f0, trans_station_point, rec_station_point)
        est_doppler_function = interp1d(est_doppler[1:,0], est_doppler[1:,1])

        for i in range(station['doppler'].shape[0]):  
            doppler_deviation[i] = station['doppler'][:,0][i], (station['doppler'][:,1][i] - est_doppler_function(station['doppler'][:,0][i]))**2
        
        doppler_deviations[station['name']] = doppler_deviation
        
    return doppler_deviations


def station_errors(met_params, timesteps, stations):
    """
    Calculate total error value of estimated meteor params to every station signal. 
    """    
    doppler_errors = error_func(met_params, timesteps, stations)
    total_deviation = []
    for station in doppler_errors:
        total_deviation.append(np.sum(doppler_errors[station][:,1]))
    return total_deviation

def total_error(met_params, timesteps, stations):
    """
    Calculate total error value of estimated meteor params to every station signal. 
    """    
    doppler_errors = error_func(met_params, timesteps, stations)
    total_deviation = 0
    for station in doppler_errors:
        total_deviation += np.sum(doppler_errors[station][:,1])
    return total_deviation

data_file = np.load("station_data.npz")
timesteps = data_file['timesteps']
stations = data_file['stations']

creator.create("FitnessMin", base.Fitness, weights=(-1.0,-1.0,-1.0,-1.0,-1.0,-1.0,-1.0,-1.0,-1.0,-1.0,-1.0,))
creator.create("Individual", array.array, typecode='d', fitness=creator.FitnessMin)

toolbox = base.Toolbox()
#pool = multiprocessing.Pool()
#toolbox.register("map", pool.map)

# Attribute generator
toolbox.register("indices", make_deap_meteor )

# Structure initializers
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evalTSP(individual):
    met_params = np.array(individual)
    return station_errors(met_params, timesteps, stations)

toolbox.register("mate", tools.cxOnePoint)
toolbox.register("mutate", tools.mutGaussian, mu = 0, sigma = (500000, 500000, 500000, 5000, 5000, 5000), indpb=1.0)
#toolbox.register("select", tools.selRandom)
#toolbox.register("select", tools.selBest)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("evaluate", evalTSP)
toolbox.register("generate", toolbox.population)

pop = toolbox.population(n=50)

hof = tools.HallOfFame(1)
stats = tools.Statistics(lambda ind: ind.fitness.values)
stats.register("min", np.min)
stats.register("sum", np.sum)

while True:
    #algorithms.eaSimple(pop, toolbox, 0.7, 0.5, 10, stats=stats, halloffame=hof, verbose=True)
    #pop, log = algorithms.eaMuPlusLambda(pop, toolbox, cxpb=0.5, mutpb=0.5, ngen=1000, stats=stats, halloffame=hof, verbose=True, mu=10, lambda_=50)
    pop, log = algorithms.eaMuCommaLambda(pop, toolbox, cxpb=0.5, mutpb=0.5, ngen=200, stats=stats, halloffame=hof, verbose=True, mu=10, lambda_=100)
    #pop, log = algorithms.eaGenerateUpdate(toolbox, ngen=100, stats=stats, halloffame=hof, verbose=True)

    print pop
    print hof

    est_params = np.array(hof[0])
    error_value = total_error(est_params, timesteps, stations)
    print error_value

    previous_parameters = np.load("estimated_parameters.npy")
    previous_error = total_error(previous_parameters, timesteps, stations)
    if error_value < previous_error:
        np.save("estimated_parameters.npy", np.array(hof[0]))
    else:
        pop = toolbox.population(n=50)

    print previous_error
    print "next cycle started..."


