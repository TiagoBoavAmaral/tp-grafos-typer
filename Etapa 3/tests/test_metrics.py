import unittest

from analysis.metrics import (
    betweenness_centrality,
    compute_metrics,
    degree_centrality,
    density,
    eigenvector_centrality,
    pagerank,
    _GraphIndex,
)
from graph import AdjacencyListGraph
from graph.utils import add_or_accumulate_edge

# Testes unitários para as métricas de grafos, cobrindo casos simples como triângulos, estrelas e caminhos lineares. Verificam propriedades esperadas como normalização, positividade e relações relativas entre vértices em estruturas conhecidas. 
class MetricsTests(unittest.TestCase):

    # Método auxiliar para criar um índice de grafo a partir de um grafo de teste, facilitando a reutilização do código de criação de índices em vários testes.
    def _index(self, g: AdjacencyListGraph) -> _GraphIndex:
        return _GraphIndex.from_graph(g)

    # Testa a densidade de um triângulo dirigido, que deve ser 3 arestas divididas pelo máximo possível de 6 (3 vértices * 2 direções).
    def test_density_directed_triangle(self):
        g = AdjacencyListGraph(3)
        g.addEdge(0, 1)
        g.addEdge(1, 2)
        g.addEdge(2, 0)
        self.assertAlmostEqual(density(self._index(g)), 3 / 6)

    # Testa a centralidade de grau em uma estrela dirigida, onde o centro tem grau máximo (3) e as pontas têm grau zero.
    def test_degree_centrality_star_out(self):
        g = AdjacencyListGraph(4)
        g.addEdge(0, 1)
        g.addEdge(0, 2)
        g.addEdge(0, 3)
        deg = degree_centrality(self._index(g))
        self.assertAlmostEqual(deg[0], 1.0)
        self.assertAlmostEqual(deg[1], 0.0)

    # Testa a centralidade de autovetor em uma estrela dirigida, onde o centro deve ter a maior centralidade devido à sua posição de influência sobre os outros vértices.
    def test_eigenvector_star_center_highest(self):
        g = AdjacencyListGraph(4)
        g.addEdge(0, 1)
        g.addEdge(0, 2)
        g.addEdge(0, 3)
        eig = eigenvector_centrality(self._index(g))
        self.assertGreater(eig[0], eig[1])
        self.assertGreater(eig[0], eig[2])
        self.assertGreater(eig[0], eig[3])

    # Testa o PageRank em um ciclo dirigido, onde todos os vértices devem ter a mesma pontuação devido à simetria do grafo. Verifica também que as pontuações são positivas e normalizadas para somar 1.
    def test_pagerank_positive_and_normalized(self):
        g = AdjacencyListGraph(3)
        g.addEdge(0, 1)
        g.addEdge(1, 2)
        g.addEdge(2, 0)
        pr = pagerank(self._index(g))
        self.assertAlmostEqual(sum(pr.values()), 1.0, places=5)
        self.assertTrue(all(v > 0 for v in pr.values()))

    # Testa a centralidade de intermediação em um caminho linear, onde o vértice do meio deve ter a maior centralidade, pois é o único que conecta os outros dois vértices.
    def test_betweenness_path_middle_highest(self):
        g = AdjacencyListGraph(3)
        g.addEdge(0, 1)
        g.addEdge(1, 2)
        bet = betweenness_centrality(self._index(g))
        self.assertGreater(bet[1], bet[0])
        self.assertGreater(bet[1], bet[2])

    # Testa a função compute_metrics para garantir que todas as métricas são calculadas e retornadas corretamente, e que as centralidades de autovetor são positivas e somam mais que zero, indicando que o cálculo foi realizado sem erros.
    def test_compute_metrics_includes_eigenvector(self):
        g = AdjacencyListGraph(4)
        add_or_accumulate_edge(g, 0, 1, 2)
        add_or_accumulate_edge(g, 1, 2, 3)
        add_or_accumulate_edge(g, 2, 3, 1)
        add_or_accumulate_edge(g, 0, 3, 1)

        m = compute_metrics(g)
        self.assertGreaterEqual(m.density, 0.0)
        self.assertLessEqual(m.density, 1.0)
        self.assertEqual(len(m.degree_centrality), 4)
        self.assertEqual(len(m.pagerank), 4)
        self.assertEqual(len(m.eigenvector_centrality), 4)
        self.assertEqual(len(m.communities), 4)
        self.assertTrue(all(v >= 0 for v in m.eigenvector_centrality.values()))
        self.assertGreater(sum(m.eigenvector_centrality.values()), 0.0)

# Executa os testes unitários quando o script é executado diretamente, permitindo a verificação automática das métricas implementadas.
if __name__ == "__main__":
    unittest.main()
