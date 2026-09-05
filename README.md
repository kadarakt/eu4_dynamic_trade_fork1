# eu4_dynamic_trade (beta)

I have changed a few things about this awesome project (it was all vibecoded with gemini, i don't know how to code). Hopefully it is easier to setup than the original (i had a lot of trouble there personally). The 4 major changes are:
1. entry.py now looks at all of your drives to locate your folders. If you struggle to open the program like me here is what I did: install python, go to your address bar on file explorer (something like D:\Downloads\eu4_dynamic_trade-0.8.1), click on it and type "cmd", then type "python enter.py" (both without the apostrophes) and click enter. It should open up the program and allow you to assign your folders.
2. Trade now flows from weaker nodes to stronger ones (in the original code trade nodes flowed from the strongest to the weakest, so strong nodes would flow into the middle of nowhere where sometimes there isn't even anyone to collect the node. i couldn't figure out why this was the case in the original)
3. End nodes must be 4 nodes apart (to prevent all end nodes from hugging each other like basegame venice genoa english channel. if you don't mind that or want them even further apart go into main.py and edit min_hops = 4 to something else like 0 or 1)
4. Inland nodes are only 80% as strong as coastal ones (can also be quickly changed by going into main.py and adjusting score.scores[i] *= 0.80)

   Original text below
   
A program to generate trade node mod for Europa Universalis 4.

1. It reads the base 00_tradenodes.exe to extract trade node data
2. It reads the specified EU4 save, and extracts relevant world data to use as reference point.
3. It then decides if it should reverse each arrow in node connections according to the specified flow rules.
4. Then it saves new 00_tradenodes.exe as a new mod called dynamic_trade.

It does not
 - allow you to have your trade direction change within a session

But it does
 - allow you to update trade direction between sessions by rerunning the program with new save data and returning to main menu of EU4.

### How to use
 1. Specify the path and name of save game to use as reference for dynamic trade direction.
 2. Specify path to EU4 mod folder if needed. The program should detect the correct directory for you, but if not then manually select it.
 3. Specify path to base tradenodes folder if needed.
 4. Change flow rules according to your preference.
    
    4.1 n_end_nodes: is only used if end_node_restriction is restricted. This fixes the strongest n_end_nodes as end nodes, the other nodes flow into them based on proximity.

    4.2 end_node_restriction: if restricted, uses n_end_nodes. If unrestricted, there will likely be local end nodes and local source nodes all over the place, and the Cape will likely be a source node.

    4.3 flow rules: choose 5 from 16 implemented flow rules. If is possible to choose fewer than 5 simply by repeating the rules.
        Rules are applied in order in a stratified manner. The subsequent rule is only used if the preceding rules all result in a tie.

        - 'Country' rules will have 'strongest' countries pull trade towards their main trade port.
            - Development has countries strength determined by total development
            - Power has countries strength determined by great power rating (development * institution penalty)
            - Cooperative will have countries collecting in the same nodes pool their power together to influence flow.
            - without Cooperative, only the strongest country in a node does the trade-pulling.
            - Mercantilism will have countries' strength multiplied by their mercantilism
        - non-Country rules will use raw status of node to influence flow.
            - Total will sum all the relevant stats from all the provinces in a node
            - Average will instead use the average (total / number of provinces)
            - Quadratic will sum the relevant stats quadratically, that is the values are squared before summing/averaging. A relevant statistical term is geometric mean.

 5. reload_save_data: when checked, will always reload and recompiles save data from specified path. When not checked, will use the data from the last run (if your last run if from previous version of the dynamic_trade mod, using old data won't work)
 6. Click 'generate mod', which will attempt to generate a mod called 'dynamic_trade' if it is not already present, otherwise it updates it.
 7. 'save settings' is there if you just want to save your new settings. 'generate mod' itself already saves new settings for you.
 8. Wait until the script is done. (should take ~2 minutes with reload save data, and instantaneously if without)
 9. Feel free to close the program, or inspect/test the result, change the settings, and try again.
 10. log file can be found in logfile.txt in the same folder as the program.

### Python Users
Python users can alternatively run 'entry.py'.
    
