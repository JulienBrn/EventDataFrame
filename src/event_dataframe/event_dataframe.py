import pandas as pd
from typing import List, Tuple, Any, Dict
import logging

logger=logging.getLogger(__name__)

class ChannelInfo:
    name: str
    type: str
    draw_color:str = None
    start_value: Any | None
    metadata: Any | None
    def __init__(self, name:str, type: str, start_value=None, metadata=None):
        self.name=name
        if type != "trigger" and type != "state":
            logger.error("Invalid channel type {} for channel {}".format(type, name))
        self.type=type
        self.start_value = start_value
        self.metadata=metadata

    def __str__(self):
        return "{}:{}".format(self.name, self.type)
    
    def __repr__(self):
        return "{}:{}".format(self.name, self.type)
    
    def copy(self):
        return ChannelInfo(self.name, self.type, self.start_value, self.metadata)
     
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
        if start_value!=None:
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
        return {n:c.copy() for n,c in self._channels.items()}
    
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
        from src.event_dataframe.draw_events import draw_events

        return draw_events(self._d, self.channels, ax)
            
    
