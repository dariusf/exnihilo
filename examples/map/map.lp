%% vertex(id)
vertex(1..3).

%% edge(a, b)
1 { edge(V1,V2) } :- vertex(V1), vertex(V2).