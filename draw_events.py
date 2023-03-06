import matplotlib.pyplot as plt
from enum import Enum
from typing import Dict, List, Tuple
import pandas as pd
import logging

logger=logging.getLogger(__name__)


class DrawOpt:
    draw_color: str = None
    type: str = None

def get_event_list(dataframe: pd.DataFrame):
    return dataframe["event_name"].unique().tolist()

def draw_events(d: pd.DataFrame, channels_opt:Dict[str,DrawOpt] = {}, ax = None):
        if not ax:
            _, ax = plt.subplots()
            
        l_ev = get_event_list(d)
        for i,n in enumerate(l_ev):
            if n=="END":
                continue
            if not n in channels_opt:
                channels_opt[n] = DrawOpt()
            if channels_opt[n].draw_color==None:
                channels_opt[n].draw_color="C"+str(i)
            if channels_opt[n].type==None:
                if d.loc[d["event_name"]==n, "value"].isnull().values.any():
                    channels_opt[n].type="trigger"
                else:
                    channels_opt[n].type="state"

        logger.debug(channels_opt)
        ax.set_ylim([0, len(channels_opt)])
        for i,n in enumerate(channels_opt.keys()):
            if channels_opt[n].type=="state":
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
                    
                    ax.hlines(hliney.iloc[:-1], hlines.iloc[:-1], hlines.iloc[1:], color=channels_opt[n].draw_color)
                    ax.hlines(hliney.iloc[-1:], hlines.iloc[-1:], [d["T"].max()], color=channels_opt[n].draw_color)
                    ax.vlines(vlinesx.iloc[1:], vlines.iloc[:-1], vlines.iloc[1:], color=channels_opt[n].draw_color)
            elif channels_opt[n].type=="trigger":
                ax.vlines(d["T"][d["event_name"]==n], i+0.1, i+0.9, color=channels_opt[n].draw_color)  
            else:
                logger.error("Unsupported state {}".format(channels_opt[n].type))    
        ax.spines[["left", "top", "right"]].set_visible(False)
        ax.set_yticks([0.5 + i for i, _ in enumerate(channels_opt)], [n for n in channels_opt.keys()])
        for n,tick in zip(channels_opt.keys(), plt.gca().get_yticklabels()):
            tick.set_color(channels_opt[n].draw_color)
        ax.tick_params(axis="y", length=0)
        ax.set_xlabel("time (s)")
        ax.margins(y=0.3)
        return ax