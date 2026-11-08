# But what is a neural network? | Deep learning chapter 1

````{tabs}
```{tab} Abstract
This video introduces the fundamental structure of a neural network using the classic task of handwritten digit recognition. It begins by contrasting the effortless visual recognition in the human brain with the difficulty of programming a computer to do the same, motivating the use of neural networks. The presenter builds a 'vanilla' neural network from scratch to recognize digits, explaining how neurons hold numerical activations between 0 and 1, arranged in layers of input, hidden, and output neurons.
```
```{tab} Key Insights

- A neural network processes data through layers where activations in one layer determine the activations of the next.

- Hidden layers are hypothesized to learn hierarchical features: lower layers detect edges, while higher layers combine these into loops and patterns.

- Each connection between neurons has a weight, and each neuron has a bias, collectively forming thousands of adjustable parameters.

- The network computes a weighted sum of inputs, adds a bias, and applies an activation function like sigmoid to constrain outputs to a specific range.

- Learning is the process of finding the correct settings for weights and biases so the network accurately maps inputs to outputs.

- The entire network acts as a single, incredibly complicated function defined by its weights and biases.

- Modern deep learning often replaces the sigmoid function with ReLU (Rectified Linear Unit) because it is easier to train than sigmoid.

- Neural networks are not just black boxes; understanding the linear algebra behind matrix-vector products helps in debugging and interpreting how they work.

```
```{tab} Deep Dive
### Core Concepts

The central concept is that a neural network is a composition of functions representing layers of neurons. An input image is flattened into a vector of pixel values fed into the first layer. Each subsequent layer transforms this data. The mechanism relies on weights, which act as knobs determining how much influence each input pixel has on a specific output neuron, and biases, which set a baseline activation threshold. The output of a layer is a vector derived from the input vector, the weight matrix, and the bias vector. This vector then passes through a non-linear activation function. The 'learning' aspect involves tuning these weights and biases so that the network correctly classifies inputs. The video suggests a hierarchical abstraction: inputs are pixels, the first hidden layer might detect simple edges, the second hidden layer might detect curves or loops made of edges, and the final layer combines these shapes into recognizable digits like '3' or '8'.


### Equations


$$a_j = sigmoid( w_{j1}x_1 + w_{j2}x_2 + ... + w_{jN}x_N + b_j )$$

$$y = sigmoid( Wx + b )$$



### Examples & Applications

The video uses a specific example of a 28x28 pixel handwritten digit '3'. It explains that recognizing this digit involves distinguishing it from other digits despite pixel variations. A concrete application discussed is the ability to decompose complex patterns: recognizing a loop requires detecting an upper arc and a lower arc. A specific hope for the network's internal logic is that one neuron in a hidden layer lights up when it detects a vertical line, another lights up for a loop, and the output layer neuron for '8' activates when the loop and line neurons are both active.
```
```{tab} Video
[![Watch on YouTube](https://img.youtube.com/vi/aircAruvnKk/maxresdefault.jpg)](https://www.youtube.com/watch?v=aircAruvnKk)

[Watch on YouTube ↗](https://www.youtube.com/watch?v=aircAruvnKk)
```
````
