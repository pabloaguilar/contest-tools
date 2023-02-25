import collections
import math
from statistics import NormalDist
from typing import Dict, List, Set

from absl import flags
from absl import logging

from concurso import Concurso
from participantes import Participante, Participantes

class Rating(object):
  """Clase encargada de actualizar ratings.

  Para una lista de concursos C, debería obtenerse el mismo resultado
  al ejecutar cualquiera de estas dos secuencias:
  ```
  # Calcular ratings en una sola pasada
  rating = Rating(algoritmo)
  rating.carga_ratings_iniciales([])
  for c in C:
    rating.actualiza_rating(c)

  # Guardard ratings hasta un punto
  rating2 = Rating(algoritmo)
  rating2.carga_ratings_iniciales([])
  for c in C[:-1]:
    rating.actualiza_rating(c)
  
  rating3 = Rating(algoritmo)
  rating3.carga_ratings_iniciales(rating.guarda_ratings())
  rating3.actualiza_rating(C[:-1])

  assertEqual(rating.guarda_ratings(), rating3.guarda_ratings())
  ```
  """
  def __init__(self, algoritmo):
    self.algoritmo = algoritmo
    self.ratings = None

  def carga_ratings_iniciales(self, participantes: Participantes):
    pass
  
  def actualiza_rating(self, concurso: Concurso):
    pass

def _WP(ratings, volatility, i, j):
  r1, v1 = ratings[i], volatility[i]
  r2, v2 = ratings[j], volatility[j]
  return 0.5 * math.erf((r1 - r2) / math.sqrt(2*(v1**2 + v2**2)))

def _Perf(x):  
  return -NormalDist().inv_cdf(x)

def TopCoder(ranking, contests, ratings, volatility):
  n = len(ratings)
  avg_rating = sum(r for r in ratings) / n
  volatility2 = sum(v**2 for v in volatility) / n
  dev2 = sum((r - avg_rating)**2 for r in ratings) / (n - 1)
  CF = math.sqrt(volatility2 + dev2)  
  ERank = [0.5 + sum(_WP(ratings, volatility, i, j)) for i in range(n) for j in range(n)]
  EPerf = [_Perf((erank - 0.5) / n) for erank in ERank]
  APerf = [_Perf((arank - 0.5) / n) for arank in ranking]
  PerfAs = [ratings[i] + CF*(APerf[i] - EPerf[i]) for i in range(n)]
  Weight = [1/(1-(.42/(contests[i] + 1) + 0.18)) - 1 for i in range(n)]
  Cap = [150 + 1500 / (contests[i] + 2) for i in range(n)]
  new_ratings = []
  new_volatility = []
  for i in range(n):
    new_rating = ratings[i] + Weight[i] * (PerfAs[i] - ratings[i])
    new_rating = min(ratings[i] + Cap[i], new_rating)
    new_rating = max(ratings[i] - Cap[i], new_rating)
    new_ratings.append(new_rating)

    new_v = math.sqrt((new_rating - ratings[i])**2 / Weight[i] + (volatility[i]**2 / (Weight[i] + 1)))
    new_volatility.append(new_v)

  return new_ratings, new_volatility

def CodeForces(ranking, contests, ratings, volatility):
  """Docs: https://codeforces.com/blog/entry/20762
  Source: https://codeforces.com/contest/1/submission/13861109
  Formal definition: https://en.wikipedia.org/wiki/Glicko_rating_system
  """
  seed = []
  # for i in ratings()


def sign(x):
  if x == 0:
    return 0
  elif x < 0:
    return -1
  else:
    return 1

RatingChange = int
StandingsRow = collections.namedtuple('StandingsRow', ['rank', 'points', 'party'])

class Contestant(object):
  def __init__(self, party: Participante, rank: int, points: float, rating: int):
    self.party = party
    self.rank = rank
    self.points = points
    self.rating = rating

    self.delta: int = 0
    self.seed: float = 0
    self.needRating: int = 0


class CodeforcesRatingCalculator(object):
  INITIAL_RATING = 1500

  def aggregateRating(self, ratingChanges: List[RatingChange]):
    rating = CodeforcesRatingCalculator.INITIAL_RATING
    for rc in ratingChanges:
      rating += rc

    return rating
 
  def getMaxRating(ratingChanges: List[RatingChange]):
    maxRating = 0 
    rating = CodeforcesRatingCalculator.INITIAL_RATING
    for rc in ratingChanges:
      rating += rc
      maxRating = max(rating, maxRating)

    return maxRating
 
  def calculateRatingChanges(self, previousRatings: Dict[Participante, int],
                             standingsRows: List[StandingsRow]) -> Dict[Participante, int]:
    contestants: List[Contestant] = []

    for standingsRow in standingsRows:
        rank = standingsRow.rank
        party = standingsRow.party
        contestants.append(Contestant(party, rank, standingsRow.points, previousRatings.get(party, CodeforcesRatingCalculator.INITIAL_RATING)))

    self.process(contestants)

    ratingChanges: Dict[Participante, int] = {}
    for contestant in contestants:
        ratingChanges[contestant.party] = contestant.delta

    return ratingChanges

  @classmethod
  def getEloWinProbability(cls, ra, rb) -> float:
    return 1.0 / (1 + math.pow(10, (rb - ra) / 400.0))
 
  def getSeed(self, contestants: List[Contestant], rating: int) -> float:
      result = 1
      for other in contestants:
          result += self.getEloWinProbability(other.rating, rating)
      return result
 
  def getRatingToRank(self, contestants: List[Contestant], rank: float) -> int:
    left = 1
    right = 8000

    while (right - left > 1):
      mid = (left + right) / 2

      if self.getSeed(contestants, mid) < rank:
          right = mid
      else:
          left = mid

    return left
 
  def reassignRanks(self, contestants: List[Contestant]):
    self.sortByPointsDesc(contestants)

    for contestant in contestants:
      contestant.rank = 0
      contestant.delta = 0

    n = len(contestants)
    first = 0
    points = contestants[0].points
    for i in range(1, n):
      if contestants[i].points < points:
        for j in range(first, i):
          contestants[j].rank = i
        first = i
        points = contestants[i].points

    # Assign the remaining ranks
    rank = n
    for j in range(first, n):
      contestants[j].rank = rank

  @classmethod
  def sortByPointsDesc(cls, contestants: List[Contestant]):
    contestants.sort(key=lambda c: c.points, reverse=True)

  @classmethod
  def sortByRatingDesc(cls, contestants: List[Contestant]):
    contestants.sort(key=lambda c: c.rating, reverse=True)

  def process(self, contestants: List[Contestant]):
    if not contestants:
      return

    self.reassignRanks(contestants)

    for a in contestants:
      a.seed = 1
      for b in contestants:
        if a != b:
          a.seed += self.getEloWinProbability(b.rating, a.rating)

    for contestant in contestants:
      midRank = math.sqrt(contestant.rank * contestant.seed)
      contestant.needRating = self.getRatingToRank(contestants, midRank)
      contestant.delta = (contestant.needRating - contestant.rating) / 2

    self.sortByRatingDesc(contestants)

    # Total sum should not be more than zero.
    n = len(contestants)
    total = sum(c.delta for c in contestants)
    inc = -total / n - 1
    for contestant in contestants:
      contestant.delta += inc

    # Sum of top-4*sqrt should be adjusted to zero.
    sum4 = 0
    zeroSumCount = min(int(4 * round(math.sqrt(n))), n)
    for i in range(zeroSumCount):
        sum4 += contestants[i].delta

    inc = min(max(-sum4 / zeroSumCount, -10), 0)
    for contestant in contestants:
        contestant.delta += inc

    self.validateDeltas(contestants)

  def validateDeltas(self, contestants: List[Contestant]):
    self.sortByPointsDesc(contestants)

    n = len(contestants)
    for i in range(n):
      ri = contestants[i].rating
      di = contestants[i].delta
      for j in range(i + 1, n):
        rj = contestants[j].rating
        dj = contestants[i].delta
        if ri > rj:
          assert ri + di >= rj + dj, (
            "First rating invariant failed: " + contestants[i].party + " vs. " + contestants[j].party + ".")

        if ri < rj:
          if di < dj:
            print(1)

          assert di >= dj, (
            "Second rating invariant failed: " + contestants[i].party + " vs. " + contestants[j].party + ".")
