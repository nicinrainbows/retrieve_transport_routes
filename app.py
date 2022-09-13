import argparse
from src import mrt
from src import bus

def generate_mrt_data(route_ids=None):
    mrt_obj = mrt(route_ids)
    mrt_df = mrt_obj._retrieve_mrt_routes()
    mrt_df.to_csv('./data/mrt_data.csv', index=False)
    return mrt_df

def generate_bus_data(API=None):
    bus_obj = bus(API)
    bus_obj._retrieve_busnums()
    print('Retrieved bus numbers!')
    bus_obj._retrieve_busids()
    print('Retrieved bus IDs!')
    bus_df = bus_obj._retrieve_bus_routes()
    bus_df.to_csv('./data/bus_data.csv', index=False)
    return bus_df

def main():
    parser = argparse.ArgumentParser(description='Generate bus and/or mrt data')
    parser.add_argument('-bus', '--bus', default='y', choices=['y', 'n'], required=True)
    parser.add_argument('-bus_api', '--bus_api', default=None, type=str)
    parser.add_argument('-mrt', '--mrt', default='y', choices=['y', 'n'], required=True)

    args = parser.parse_args()

    if args.bus == 'y':
        if args.bus_api == None:
            raise ValueError('Please specify a LTA Datamall API.')
        generate_bus_data()
        print('Done with generation of bus data. Please see Data folder for the updated file.')
    
    if args.mrt == 'y':
        generate_mrt_data()
        print('Done with generation of mrt data. Please see Data folder for the updated file.')

if __name__ == '__main__':
    main()