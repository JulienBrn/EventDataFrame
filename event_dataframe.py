import pandas as pd
from typing import List, Tuple, Any, Dict
import logging

logger=logging.getLogger(__name__)

class ChannelInfo:
    name: str
    type: str
    start_value: Any | None
    metadata: Any | None
    def __init__(self, name:str, type: str, start_value=None, metadata=None):
        self.name=name
        if type != "trigger" and type != "state":
            logger.error("Invalid channel type {} for channel {}".format(type, name))
        self.type=type
        self.start_value = start_value
        self.metadata=metadata
     
class EventData:
    _d : pd.DataFrame
    _channels: Dict[str, ChannelInfo] = {}
    _is_updated: bool = False
    _duration: float
    
    def __init__(self, duration):
        self._d = pd.DataFrame([[duration, "END", None, None, 0]], columns=["T", "event_name", "value", "old_value", "duration"])
        self._duration=duration
       
    def add_channel(self, name: str, type: str, start_value: Any=None):
        if name in self._channels:
            logger.error("Add channel called with {} but a channel with the same name already exists.".format(name))
            raise BaseException("Problem")
        self._channels[name] = ChannelInfo(name, type, start_value)
        if type=="state":
            self._d[name] = None
        if start_value:
             self.add_event(0, name, start_value)
        self._is_updated=False
            
    def add_event(self, t: float, channel: str, val:Any):
        if not channel in self._channels:
            logger.error("Add event of undeclared channel {}".format(channel))
            raise BaseException("Problem")
        self._d = pd.concat([self._d, pd.DataFrame.from_records([{"T": t, "event_name": channel, "value": val}])], ignore_index=True)
        self._is_updated=False
        
    @property
    def dataframe(self):
        self._update()
        return self._d.copy()
    
    @property
    def channels(self):
        return self._channels.copy()
    
    def __str__(self):
        return self.dataframe.__str__()
    
    def __repr__(self):
        return self.dataframe.__repr__()
    
    def to_string(self):
        return self.dataframe.to_string()
    
    @property 
    def nb_events(self):
        return self._d["event_name"].count()
    
    def get_summary(self):
        res=""
        res+="Channels are (total={}):\n".format(len(self._channels))
        for c in self._channels.keys():
            res+="  - {} of type {} with {} events\n".format(c, self._channels[c].type, (self._d.loc[self._d["event_name"]==c, "event_name"]).count())
        return res
    
    
    def _update(self):
        if not self._is_updated:
            # Sort on T
            self._d.sort_values(by=['T'], inplace=True, ignore_index=True)
            # Compute old_value
            for name in self._channels.keys():
                if self._channels[name].type=="state":
                    # self._d.loc[self._d["event_name"]==name, "old_value"]=self._d.loc[self._d["event_name"]==name, "value"].shift(1, fill_value=self._channels[name].start_value)
                    self._d.loc[self._d["event_name"]==name, "old_value"]=self._d.loc[self._d["event_name"]==name, "value"].shift(1)
            #Removing duplicates              
            self._d = self._d[self._d["value"] != self._d["old_value"]]
            #Computing duration and column state
            for name in self._channels.keys():
                if self._channels[name].type=="state":
                    self._d.loc[self._d["event_name"]==name, "duration"]=(
                        self._d.loc[self._d["event_name"]==name, "T"].shift(-1, fill_value=self._duration)
                        - self._d.loc[self._d["event_name"]==name, "T"]
                    )
                    self._d.loc[self._d["event_name"]==name, name]=self._d.loc[self._d["event_name"]==name, "value"]
                    self._d[name].ffill(inplace=True)
                    
            # Handling start columns state
            # for name in self._channels.keys():
            #     if self._channels[name].type=="state":        
            #         if self._channels[name].start_value != None:
            #             for i in range(self.nb_events):
            #                 if self._d["event_name"].iat[i]==name:
            #                     self._d[name].iloc[0:i]=self._channels[name].start_value
            #                     break
            
            self._is_updated=True
            
    def draw_plot(self, ax = None):
        self._update()
        import matplotlib.pyplot as plt
        if not ax:
            _, ax = plt.subplots()
            
        ax.yaxis.set_visible(False)
        ax.set_ylim([0, len(self._channels)])
        for i,n in enumerate(self._channels.keys()):
            if self._channels[n].type=="state":
                d = self._d
                max_val = d["value"][d["event_name"]==n].max()
                min_val = d["value"][d["event_name"]==n].min()
                    
                
                def position(val):
                    if max_val!=min_val:
                        return i+0.1 + ((val-min_val)/(max_val-min_val))*0.8
                    else:
                        return i+0.5+val*0
                
                if max_val or max_val==0:
                    hliney=position(d["value"][d["event_name"]==n])
                    hlines=d["T"][d["event_name"]==n]
                    
                    vlinesx=(d["T"][d["event_name"]==n])
                    vlines=position(d["value"][d["event_name"]==n])
                    
                    ax.hlines(hliney.iloc[:-1], hlines.iloc[:-1], hlines.iloc[1:], color="C"+str(i))
                    ax.hlines(hliney.iloc[-1:], hlines.iloc[-1:], [d["T"].max()], color="C"+str(i))
                    ax.vlines(vlinesx.iloc[1:], vlines.iloc[:-1], vlines.iloc[1:], color="C"+str(i))
            else:
                ax.vlines(d["T"][d["event_name"]==n], i+0.1, i+0.9, color="C"+str(i))            
            ax.text(0, i+0.5, n+"    ", horizontalalignment="right", color="C"+str(i))
        ax.spines[["left", "top", "right"]].set_visible(False)
        ax.set_xlabel("time (s)")
        ax.margins(y=0.3)
        return ax
    
    
if __name__ == "__main__":
    import beautifullogger
    import matplotlib.pyplot as plt
    import matplotlib
    # matplotlib.use('Qt5Agg')
    beautifullogger.setup()
    
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    
    ed = EventData(100)
    ed.add_channel("reward", type="state", start_value=4)  
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
    ed.add_event(20, "reward", 1)
    print(ed.get_summary())
    print(ed.to_string())
    
    fig, ax = plt.subplots()
    ed.draw_plot(ax)
    plt.show()