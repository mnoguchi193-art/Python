# Python

Python の学習・参照用リポジトリです。

A Python learning and reference repository.

## 構成 / Structure

| Directory | Contents |
|---|---|
| [basics/](basics/) | data types, control flow, functions, comprehensions |
| [data_structures/](data_structures/) | stack, queue, linked list, binary search tree |
| [utilities/](utilities/) | file I/O, string helpers, datetime (JST) |
| [standard_library/](standard_library/) | collections, itertools, pathlib demos |
| [patterns/](patterns/) | design patterns, e.g. command pattern (remote control) |
| [political_science/](political_science/) | computational political science: voting methods, power indices, opinion dynamics |
| [economics/](economics/) | computational economics: game theory, auction theory, stable matching |
| [law/](law/) | computational law: defeasible legal reasoning, precedent networks, fair division |
| [medicine/](medicine/) | computational medicine: SIR epidemics, survival analysis, diagnostic test evaluation |
| [sociology/](sociology/) | computational sociology: Schelling segregation, social network analysis, threshold cascades |
| [psychology/](psychology/) | computational psychology: Rescorla-Wagner learning, drift diffusion, signal detection |
| [philosophy/](philosophy/) | computational philosophy: propositional logic, modal logic (Kripke), abstract argumentation |
| [history/](history/) | computational history: cliodynamics (secular cycles), radiocarbon dating, seriation |
| [literature/](literature/) | computational literary studies: stylometry (Burrows's Delta), narrative arcs, Zipf's law |
| [meteorology/](meteorology/) | computational meteorology: Lorenz chaos, ensemble forecasting, atmospheric thermodynamics |
| [neuroscience/](neuroscience/) | computational neuroscience: integrate-and-fire neuron, Hopfield memory, STDP |
| [cognitive_neuroscience/](cognitive_neuroscience/) | predictive coding, Bayesian cue integration, population decoding |
| [ai/](ai/) | artificial intelligence from scratch: neural network (backprop), self-attention, Q-learning, INT8 quantization |
| [computer_science/](computer_science/) | advanced CS: Bloom filter, consistent hashing, RSA cryptography |
| [information_science/](information_science/) | information theory, Huffman coding, Hamming error correction |
| [robotics/](robotics/) | robotics (sense-plan-act): arm kinematics, A* path planning, Kalman filter |
| [quantum_computing/](quantum_computing/) | qubit simulator, Grover's search, CHSH/Bell inequality, error correction, the QEC threshold |
| [semiconductors/](semiconductors/) | carrier statistics, PN-junction diode, MOSFET characteristics |
| [aerospace/](aerospace/) | orbital mechanics, the rocket equation, aerodynamics & standard atmosphere |
| [astronomy/](astronomy/) | stellar physics, cosmology (Hubble's law), exoplanet detection |
| [physics/](physics/) | special relativity, the Ising model (phase transition), quantum well & tunneling |
| [mathematics/](mathematics/) | number theory, the Mandelbrot set, automatic differentiation |
| [chemistry/](chemistry/) | equation balancing, reaction kinetics, acid-base equilibrium |
| [biology/](biology/) | sequence alignment, the central dogma, population genetics |

## 実行方法 / How to Run

```bash
python basics/data_types.py
python data_structures/linked_list.py
python standard_library/collections_demo.py
python patterns/remote_control.py
python political_science/voting_methods.py
python economics/game_theory.py
python law/legal_reasoning.py
python medicine/epidemic_sir.py
python sociology/schelling_segregation.py
python psychology/rescorla_wagner.py
python philosophy/propositional_logic.py
python history/cliodynamics.py
python literature/stylometry.py
python meteorology/lorenz_system.py
python neuroscience/integrate_and_fire.py
python cognitive_neuroscience/predictive_coding.py
python ai/self_attention.py
python computer_science/bloom_filter.py
python information_science/information_theory.py
python robotics/kinematics.py
python quantum_computing/qubit_simulator.py
python semiconductors/carrier_statistics.py
python aerospace/orbital_mechanics.py
python astronomy/stellar_physics.py
python physics/special_relativity.py
python mathematics/number_theory.py
python chemistry/equation_balancer.py
python biology/sequence_alignment.py
```

外部ライブラリは不要です (標準ライブラリのみ使用)。

## テスト / Tests

すべてのモジュールが正常に実行されることを確認するスモークテスト。

A smoke test runs every example module in a subprocess and asserts a clean exit,
so a regression in any example is caught automatically.

```bash
python -m unittest discover tests
# or
python tests/test_smoke.py
```

