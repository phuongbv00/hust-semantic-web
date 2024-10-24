# HUST Semantic Web

## Introduction

### Ontology design

![](./docs/ontology.drawio.svg)

### Architecture

![](./docs/arch.drawio.png)

## Setup

### Data process

### Open data linking (5 stars)

#### Extract open data from DBpedia

1. Go to [https://dbpedia.org/sparql](https://dbpedia.org/sparql)
2. Paste the under query
    ```sparql
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dbp: <http://dbpedia.org/property/>

    SELECT ?uri ?name ?brandName ?brandFoundDate ?releaseDate ?osName
    WHERE {
        ?uri a dbo:Device ;
        rdfs:label ?name .
        OPTIONAL {
            ?uri dbp:brand ?brand .
            ?brand dbp:name ?brandName .
            ?brand dbo:foundingDate ?brandFoundDate } .
        OPTIONAL { ?uri dbo:releaseDate ?releaseDate } .
        OPTIONAL {
            ?uri dbo:operatingSystem ?os .
            ?os dbp:name ?osName } .
        FILTER (lang(?name) = "en") .
        FILTER (
            regex(str(?uri), "iPhone", "i") || 
            regex(str(?uri), "iPad", "i") || 
            regex(str(?uri), "Galaxy", "i") || 
            regex(str(?uri), "Pixel", "i") ||
            regex(str(?uri), "Oppo", "i") || 
            regex(str(?uri), "Xiaomi", "i") ||
            regex(str(?uri), "Realme", "i") ||
            regex(str(?uri), "OnePlus", "i")
        ) .
    }
    LIMIT 2000
    ```
3. Execute the query with Results Format in **CSV**
4. Save as ```/res/dbpedia.csv```

## SPARQL queries example

### Find smartphones with brand name is 'Apple'

```sparql
PREFIX onto: <http://www.semanticweb.org/hust/master/2024/10/ontologies/smartphone.owl#>
SELECT ?smartphone ?name ?os
WHERE {
    ?smartphone a onto:SmartPhone .
    ?smartphone onto:hasBrand ?brand .
    ?brand onto:name "Apple" .
    ?smartphone onto:name ?name .
    OPTIONAL {
        ?smartphone onto:hasOS ?os
    } .
}
```

### Find Samsung Galaxy smartphones

```sparql
PREFIX onto: <http://www.semanticweb.org/hust/master/2024/10/ontologies/smartphone.owl#>
SELECT ?smartphone ?name
WHERE {
    ?smartphone a onto:SmartPhone .
    ?smartphone onto:name ?name .
    FILTER contains(?name, "Galaxy")
}
```

### Find smartphones have mainCamera video contains '8K'

```sparql
PREFIX onto: <http://www.semanticweb.org/hust/master/2024/10/ontologies/smartphone.owl#>
SELECT ?smartphone ?video
WHERE {
    ?smartphone a onto:SmartPhone .
    ?smartphone onto:hasCamera ?mainCamera .
    ?mainCamera a onto:MainCamera .
    ?mainCamera onto:video ?video .
    FILTER contains(?video, "8K")
}
```

### Find smartphones with ```owl:sameAs``` relationships

```sparql
PREFIX onto: <http://www.semanticweb.org/hust/master/2024/10/ontologies/smartphone.owl#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
SELECT ?smartphone ?sameAs
WHERE {
   ?smartphone a onto:SmartPhone .
   OPTIONAL { ?smartphone owl:sameAs ?sameAs } .
}
ORDER BY DESC(?sameAs)
```

### Select all pairs of predicate and object of ```iphone_14_pro```

```sparql
SELECT ?predicate ?object
WHERE {
  <http://www.semanticweb.org/hust/master/2024/10/ontologies/smartphone.owl#iphone_14_pro> ?predicate ?object .
}
```