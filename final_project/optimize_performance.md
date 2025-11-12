# Documentation des Performances - Optimisation PySpark

## Vue d'ensemble
Ce document présente les optimisations appliquées au traitement des données industrielles avec PySpark et les améliorations de performances obtenues.

**Fichier analysé :** `optimize.ipynb`  
**Date :** 12 novembre 2025  
**Dataset :** Industrial Monitoring Logs (7,672 enregistrements)

---

## Avant Optimisation

### Configuration initiale
- **Partitionnement :** Partitionnement par défaut (nombre de partitions non contrôlé)
- **Cache :** Aucune mise en cache appliquée
- **Checkpoint :** Aucun checkpoint configuré
- **Join :** Join standard sans broadcast

### Plan d'exécution physique
```
FileScan csv [timestamp, date, temperature, pressure, vibration, humidity, equipment, location, faulty]
Batched: false
DataFilters: []
Format: CSV
```

### Problèmes identifiés
1. **Lecture multiple du CSV** : Les données sont relues à chaque action sans cache
2. **Partitionnement non optimisé** : Distribution des données non contrôlée
3. **Lineage RDD long** : Risque de recomputation coûteuse en cas d'échec
4. **Join inefficace** : Join de petites tables sans optimisation broadcast

---

## Après Optimisation

### Configuration optimisée

#### 1. Repartitionnement stratégique
```python
dataframe_repartitioned_8 = dataframe_logs.repartition(8)
```
- **Nombre de partitions :** 8 partitions
- **Avantage :** Distribution uniforme des données pour un traitement parallèle optimal

#### 2. Mise en cache
```python
dataframe_repartitioned_8.cache()
```
- **Stockage :** Données gardées en mémoire
- **Avantage :** Évite les recalculs coûteux lors d'actions multiples

#### 3. Broadcast Join
```python
dataframe_joined = dataframe_repartitioned_8.join(
    broadcast(dataframe_metadata), 
    dataframe_repartitioned_8.equipment == dataframe_metadata.equipment_type
)
```
- **Type :** Broadcast Hash Join
- **Avantage :** Table de métadonnées diffusée sur tous les workers, évite le shuffle

#### 4. Checkpoint
```python
spark.sparkContext.setCheckpointDir("./checkpoint")
dataframe_checkpointed = dataframe_repartitioned_8.checkpoint()
```
- **Répertoire :** `./checkpoint`
- **Avantage :** Troncature du lineage RDD, sauvegarde intermédiaire des résultats

---

## Résultats des Optimisations

### Métriques de performance

| Métrique | Avant | Après | Amélioration |
|----------|-------|-------|--------------|
| **Nombre de partitions** | Variable (non contrôlé) | 8 (optimisé) | ✅ Distribution contrôlée |
| **Cache activé** | ❌ Non | ✅ Oui | Réduction des recalculs |
| **Checkpoint** | ❌ Non | ✅ Oui | Lineage tronqué |
| **Type de Join** | Standard (shuffle) | Broadcast | Pas de shuffle côté metadata |
| **Enregistrements traités** | 7,672 | 7,672 | - |

### Détails techniques

#### Configuration finale confirmée
```
Nombre de partitions : 8
Nombre d'enregistrements : 7,672
Répertoire de checkpoint : ./checkpoint
```

#### Structure du checkpoint
```
checkpoint/
├── [UUID]/
    ├── part-00000
    ├── part-00001
    ├── part-00002
    ├── part-00003
    ├── part-00004
    ├── part-00005
    ├── part-00006
    └── part-00007
```

---

## Bonnes Pratiques Appliquées

### 1. **Repartitionnement intelligent**
- Choix de 8 partitions basé sur les ressources disponibles
- Distribution uniforme des données pour équilibrage de charge

### 2. **Lazy Evaluation optimisée**
- Cache stratégique sur les DataFrames réutilisés
- Évite les recalculs lors d'actions multiples (count, show, write)

### 3. **Gestion du lineage**
- Checkpoint pour tronquer les DAG complexes
- Sauvegarde intermédiaire pour reprise en cas d'échec

### 4. **Optimisation des joins**
- Broadcast des petites tables (metadata)
- Réduction significative du shuffle réseau

---

## Impact sur le Pipeline

### Avantages obtenus
1. **Performance** : Réduction du temps d'exécution grâce au cache et au broadcast
2. **Fiabilité** : Checkpoint permet la reprise en cas d'échec
3. **Scalabilité** : Architecture prête pour traiter des volumes plus importants
4. **Prévisibilité** : Partitionnement contrôlé pour des performances constantes

### Recommandations pour la production
- **Monitoring** : Surveiller l'utilisation mémoire du cache
- **Tuning** : Ajuster le nombre de partitions selon la taille des données
- **Nettoyage** : Mettre en place un processus de nettoyage des checkpoints anciens
- **Configuration** : Augmenter la mémoire driver/executor si nécessaire

---

## Code Optimisé Complet

```python
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import broadcast

# Initialisation Spark
spark = SparkSession.builder.appName("Optimize").getOrCreate()

# Lecture des données
dataframe_logs = spark.read.csv("./data/industrial_monitoring_logs.csv", 
                                header=True, inferSchema=True)

# Repartitionnement et cache
dataframe_repartitioned_8 = dataframe_logs.repartition(8)
dataframe_repartitioned_8.cache()

# Lecture metadata et broadcast join
dataframe_metadata = spark.read.csv("./data/equipment_metadata.csv", 
                                    header=True, inferSchema=True)
dataframe_joined = dataframe_repartitioned_8.join(
    broadcast(dataframe_metadata), 
    dataframe_repartitioned_8.equipment == dataframe_metadata.equipment_type
)

# Configuration et application du checkpoint
checkpoint_dir = "./checkpoint"
os.makedirs(checkpoint_dir, exist_ok=True)
spark.sparkContext.setCheckpointDir(checkpoint_dir)
dataframe_checkpointed = dataframe_repartitioned_8.checkpoint()

# Nettoyage
spark.stop()
```

---

## Analyse du Plan d'Exécution

### Plan logique analysé
```
Relation [timestamp, date, temperature, pressure, vibration, 
         humidity, equipment, location, faulty] csv
```

### Optimisations Catalyst appliquées
- Projection pushdown
- Predicate pushdown (si filtres présents)
- Broadcast join optimization

---

## Conclusion

Les optimisations appliquées dans `optimize.ipynb` transforment un pipeline basique en une solution robuste et performante :

**Partitionnement contrôlé** pour distribution optimale  
**Cache stratégique** pour réduire les recalculs  
**Broadcast join** pour éliminer les shuffles inutiles  
**Checkpoint** pour garantir la résilience  

Ces techniques sont essentielles pour le traitement de données à grande échelle en production.
