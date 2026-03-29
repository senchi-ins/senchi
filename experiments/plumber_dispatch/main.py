from dispatch import Dispatch
from search import ProximitySearch
from agent import DispatchAgent


def main():
    # plumbers = find_nearby_plumbers("Toronto, Ontario, Canada")
    # calling_list = generate_calling_list(plumbers)
    # print(calling_list)
    sample_list = [
        {'name': 'Plumber To Your Door of Toronto', 'phone': '+12989716341'}, 
        # {'name': 'Royal Plumbing Services Ltd.', 'phone': '+14165370038'}, 
        # {'name': 'Leaside Plumbing and Heating Ltd', 'phone': '+14164238682'}
    ]

    agent_id = "agent_6001k2575skne5mbxsag2gcxcv2b"
    agent_phone_number_id = "phnum_9401k20rbabff11sry0y4ckhc1sk"

    agent = DispatchAgent(agent_id, agent_phone_number_id)
    search = ProximitySearch()
    dispatch = Dispatch(agent, search)
    dispatch.dispatch("Toronto, Ontario, Canada")


if __name__ == "__main__":
    main()
