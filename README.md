## 1. Mathematical Fundamentals

> _"A type of non-linear data structure, a graph consists of nodes and edges. Each node, also called vertices, represents an entity, while each relationship in the graph, represented as an edge, signifies a relationship between two vertices. This fundamental concept in graph theory allows us to model a wide array of real-world scenarios" — (SaWang, PuppyGraph. Jan, 2025)_

A crawler functions similarly to how a graph works. Basically, each web page behaves like a node, where a single node can point to n number of websites, and multiple nodes can point to the same website. The navigation of a crawler is based on the same principle as a graph traversal; in this case, I will base it on a breadth-first search (BFS) model.

## 2. Crawler Conceptualization

- Starts from a seed (URL) as the initial node  
- Maintains two sets:  
  - `visited`: URLs already visited  
  - `queue`: URLs pending to be visited  
- Iterates by depth levels, based on the pages discovered at each level  
- Explores all nodes at the current depth before moving on to the next one  

## 3. Crawler Module

The `Crawler` module implements a horizontal-scalable architecture, where you can create one `Crawler` module with hundreds of nodes (sharing the same memmory, but managing hundreds of asynchronous processes).

### 3.1 Requirements

- Python 3.9+
- html-to-markdown 1.16.0
- url_normalize 2.2.1
- lxml 6.0.1
- jsonlines 4.0.0
- requests 2.32.3+
- xai_sd 1.1.0+

`pip install -r requirements.txt`

### 3.2 Usage

1. Load the enviroment variable of `xai_sdk`

```python
from dotenv import load_dotenv
load_dotenv()
```

2. Initialize the crawler object with ta seed URL

```python
constructor = Crawler('https://www.geeksforgeeks.org/machine-learning/what-is-perceptron-the-simplest-artificial-neural-network/')
```

3. Start a node in the crawler object with a depth

```python
constructor.node(filename='crawled-sites.json', depth=2)
```

```txt
Depth 1/2:
    1 Sites Crawled | 82.218219 Seconds

Error HTTP https://in.linkedin.com/company/geeksforgeeks: 999
Error HTTP https://www.geeksforgeeks.org/machine-learning/machine-learning-interview-questions/)_: 404
Error HTTP https://www.geeksforgeeks.org/deep-learning/deep-learning-interview-questions/)_: 404
Error HTTP https://www.geeksforgeeks.org/deep-learning/5-deep-learning-project-ideas-for-beginners/)_: 404
Error HTTP https://www.geeksforgeeks.org/machine-learning/machine-learning-projects/)_: 404
Error HTTP https://geeksforgeeksapp.page.link/: 400
Depth 2/2:
    154 Sites Crawled | 4113.7781 Seconds
```

> You have the exctected content in the crawled-sites.jsonl file

### Remember

- You can implement multithread where all the nodes share the same memory (Crawler), but this module its not optimized to manage `race conditions`
- The `xai_sdk` can chang the API structure
