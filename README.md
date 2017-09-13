# CA

## Thesis events
### 20170901: Started working 
         * Cell on a grid capable to reproduce.
### 20170907:
         * Plotting works: unefficient way, must improve this!
         * Adding states: move, split, die. Start to work on cell dynamics and then insert the neural network
### 20170911:
         * Added new functions for moving and splitting. In principle they work regardless of the state of the
          compass (ON/OFF). Must test that.
         * Must clarify the decision making: what happens if the orientation direction is out of bounds or 
          occupied? action must fail or choose a random available spot instead?
### 20170913:
         * Started implementing the more stable and fast plotting scheme.
         * Read some articles about NN. Must:
                  * Do some research about which type of NN is adequate for the model.
                  * Is the NN used originally in the model the best for the task?
                  * SHpuld I use available libraries or write my own code for NN.
         * Think about how to record a video/timelapse if the cell structure.
