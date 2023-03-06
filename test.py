import event_dataframe as ev
import logging

if __name__ == "__main__":
    import beautifullogger
    import matplotlib.pyplot as plt

    beautifullogger.setup()
    
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    
    ed = ev.EventData(100)
    ed.add_channel("reward", type="state", start_value=0)  
    ed.add_channel("lever", type="state", start_value=3)  
    ed.add_channel("spike", type="trigger") 
    ed.add_event(4, "reward", 4) 
    ed.add_event(10, "reward", 2)
    ed.add_event(15, "reward", 1)
    ed.add_event(15, "spike", 1)
    ed.add_event(9, "spike", 1)
    ed.add_event(12, "lever", 1)
    ed.add_event(16, "reward", 1)
    ed.add_event(8, "reward", 1)
    ed.add_event(20, "reward", 2)
    print(ed.get_summary())
    print(ed.to_string())
    
    d = ed.dataframe
    d2 = d[(d["event_name"]!="reward") | ((d["event_name"]=="reward") & (d["value"] > d["old_value"]))]
    c2 = ed.channels
    c2["reward"].type="trigger"
    print(ed.channels)
    fig, ax = plt.subplots()
    from src.event_dataframe.draw_events import draw_events
    
    draw_events(d2, c2, ax)
    plt.show()