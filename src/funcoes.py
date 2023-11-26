from src.arqImport import *
from src.listasCompartilhadas import *

def regiao(nome, tipo, listaRegiao):
    encontrado = False  # Variável auxiliar para rastrear se o nome já foi encontrado
    for x in listaRegiao:
        if x.cidade == nome:
            encontrado = True
            if tipo == 'Non Resedential':
                x.incrementar_ocorrenciax(1)
            else:
                x.incrementar_ocorrenciay(1)
            x.somarTotal()
            break

    if not encontrado:  # Se o nome não foi encontrado, adicione-o à lista
        aux = Infos(nome, 0, 0, 0)
        if tipo == 'Non Resedential':
            aux.incrementar_ocorrenciax(1)
        else:
            aux.incrementar_ocorrenciay(1)
        aux.somarTotal()
        listaRegiao.append(aux)

def coordenadas(lista):
    lista2 = []
    with open('input/fullCoordenadas.csv', 'r') as arq_csv:
        read = csv.DictReader(arq_csv)
        for linha in read:
            nome = linha['nick']
            latitude = linha['lati']
            longitude = linha['long']
            latitude = latitude.replace(',', '.')
            longitude = longitude.replace(',', '.')

            #aqui faz a poda das regioes sem localização ou desertos...
            for x in lista:
                if x.cidade == nome:
                    aux = Infos(nome,x.ocorrenciax,x.ocorrenciay,x.total)
                    aux.coordenas(latitude,longitude)
                    lista2.append(aux)
                    break
    return lista2

def determinar_cor(cidade):
    if cidade.total >= 10:
        cor = 'red'
    elif 5 < cidade.total < 10:
        cor = 'orange'
    elif cidade.total <= 5:
        cor = 'yellow'
    else:
        cor = 'lightblue'
    return cor

def removerNos(G):
    nos_a_remover = [node for node, cor in nx.get_node_attributes(G, 'cor').items() if cor != 'red']
    G.remove_nodes_from(nos_a_remover)

def grafo(lista,start):
    # Criando um grafo ponderado simples
    G = nx.Graph()
    edge_data = {}
    edge_dataColor = {}

    for cidade_info in lista:
        nome = cidade_info.cidade
        ataque = cidade_info.total  
        cor =  determinar_cor(cidade_info)
        edge_dataColor[(cidade_info.cidade, cidade_info.cidade)] = cor
        G.add_node(nome, latitude=float(cidade_info.latitude), longitude=float(cidade_info.longitude), total = ataque, cor = cor)

    # Calcule e adicione as arestas (distâncias) entre as cidades com base nas coordenadas
    for cidade_info1 in lista:
        for cidade_info2 in lista:
            if cidade_info1 != cidade_info2:
                coords1 = (cidade_info1.latitude, cidade_info1.longitude)
                coords2 = (cidade_info2.latitude, cidade_info2.longitude)
                point1 = Point(coords1)
                point2 = Point(coords2)
                distancia = geodesic(point1, point2).kilometers
                G.add_edge(cidade_info1.cidade, cidade_info2.cidade, weight=distancia)
                edge_data[(cidade_info1.cidade, cidade_info2.cidade)] = distancia
        
    salvarCSV(edge_data)
    salvarCSV2(edge_dataColor)

    # Obtendo o layout para plotar o grafo
    pos = nx.spring_layout(G)
    # Plotando o grafo original
    nx.draw(G, pos, with_labels=True, node_color=[G.nodes[v].get('cor', 'lightblue') for v in G.nodes], font_color='black', font_weight='bold', node_size=700)
    plt.title("Grafo Original")
    plt.show()

    removerNos(G)
    nx.draw(G, pos, with_labels=True, node_color=[G.nodes[v].get('cor', 'lightblue') for v in G.nodes], font_color='black', font_weight='bold', node_size=700)
    plt.title("Grafo Pos corte")
    plt.show()

    agm = nx.minimum_spanning_tree(G)
    # Obtendo o layout para plotar o grafo
    pos = nx.spring_layout(agm)
    # Plotando a Árvore Geradora Mínima
    nx.draw(agm, pos, with_labels=True, node_color=[G.nodes[v].get('cor', 'lightblue') for v in agm.nodes], font_color='black', font_weight='bold', node_size=700)
    labels_agm = nx.get_edge_attributes(agm, 'weight')
    formatted_labels_agm = {edge: f"{weight:.0f}" for edge, weight in labels_agm.items()}
    nx.draw_networkx_edge_labels(agm, pos, edge_labels=formatted_labels_agm)
    plt.title("Árvore Geradora Mínima do Subgrafo")
    plt.show()

    nome, maior_ataque_bfs = bfs_maior_ataque(agm,start)
    print(f'O nó {nome} com o maior ataque tem valor: {maior_ataque_bfs}')

    df = pd.DataFrame({
        'Node': agm.nodes(),
    })
    df.to_csv('output/informacoes_da_rede.csv', index=False)
    df_edges = pd.DataFrame([(u, v, d['weight']) for u, v, d in agm.edges(data=True)], columns=['Source', 'Target', 'Distance'])
    df_edges.to_csv('output/informacoes_das_arestas.csv', index=False)
  
def salvarCSV(edge_data):
    csv_file = "output/grafo.csv"

    # Abrir o arquivo CSV em modo de escrita
    with open(csv_file, mode='w', newline='') as file:
        # Criar um escritor CSV
        writer = csv.writer(file)

        # Escrever o cabeçalho (opcional, dependendo dos requisitos)
        writer.writerow(['Source', 'Target', 'Weight'])

        # Iterar sobre as entradas do grafo_dict e escrever no arquivo CSV
        for (cidade1, cidade2), distancia in edge_data.items():
            writer.writerow([cidade1, cidade2, distancia])

    print(f"As informações foram salvas no arquivo CSV: {csv_file}")

def salvarCSV2(edge_data):
    csv_file = "output/grafo2.csv"

    # Abrir o arquivo CSV em modo de escrita
    with open(csv_file, mode='w', newline='') as file:
        # Criar um escritor CSV
        writer = csv.writer(file)

        # Escrever o cabeçalho (opcional, dependendo dos requisitos)
        writer.writerow(['Id', 'Label', 'Cor'])

        # Iterar sobre as entradas do grafo_dict e escrever no arquivo CSV
        for (cidade1, cidade2), cor in edge_data.items():
            writer.writerow([cidade1, cidade2, cor])

    print(f"As informações foram salvas no arquivo CSV: {csv_file}")

def salvarCSV3(lista):
    csv_file = "output/FullNos.csv"

    # Abrir o arquivo CSV em modo de escrita
    with open(csv_file, mode='w', newline='') as file:
        # Criar um escritor CSV
        writer = csv.writer(file)

        # Escrever o cabeçalho (opcional, dependendo dos requisitos)
        writer.writerow(['Id'])

        # Iterar sobre as entradas do grafo_dict e escrever no arquivo CSV
        for x in lista:
            writer.writerow([x.cidade])

    print(f"As informações foram salvas no arquivo CSV: {csv_file}")

def gerar_TodasLista():
    with open('input/demolition.csv', 'r') as arquivo_csv:
        leitor_csv = csv.DictReader(arquivo_csv)
        for linha in leitor_csv:
            nome = linha['locality']
            distrito = linha['district']
            tipo = linha['type_of_sturcture']
            
            regiao(nome,tipo,Full_lista)

            if distrito == 'Hebron':  #ok
                regiao(nome,tipo,listaHebron)
            
            if distrito == 'Tulkarm': #ok
                regiao(nome,tipo,listaTulkarm)
            
            if distrito == 'al-Quds': #ok
                regiao(nome,tipo,listaAlQuds)

            if distrito == 'Jericho': #ok
                regiao(nome,tipo,listaJericho)
            
            if distrito == 'Jenin': #ok
                regiao(nome,tipo,listaJenin)
            
            if distrito == 'Salfit': #ok
                regiao(nome,tipo,listaSalfit)
            
            if distrito == 'Nablus': #ok
                regiao(nome,tipo,listaNablus)

            if distrito == 'Bethlehem': #ok
                regiao(nome,tipo,listaBethlehem)

            if distrito == 'Tubas': #ok
                regiao(nome,tipo,listaTubas)

            if distrito == 'Qalqiliya': #ok
                regiao(nome,tipo,listaQalqiliya)

            if distrito == 'Ramallah and al-Bira': #ok
                regiao(nome,tipo,listaRamallah)

def adicionar_Coordenadas():
    global listaHebron, listaTulkarm, listaAlQuds, listaJericho, listaJenin, listaSalfit, listaNablus, listaBethlehem, listaTubas, listaQalqiliya, listaRamallah, Full_lista
    listaHebron = coordenadas(listaHebron)
    listaTulkarm = coordenadas(listaTulkarm)
    listaAlQuds = coordenadas(listaAlQuds)
    listaJericho = coordenadas(listaJericho)
    listaJenin = coordenadas(listaJenin)
    listaSalfit = coordenadas(listaSalfit)
    listaNablus = coordenadas(listaNablus)
    listaBethlehem = coordenadas (listaBethlehem)
    listaTubas = coordenadas(listaTubas)
    listaQalqiliya = coordenadas(listaQalqiliya)
    listaRamallah = coordenadas(listaRamallah)

def bfs_maior_ataque(grafo, inicio):
    fila = deque([(inicio, grafo.nodes[inicio]['total'])])
    visitados = set()
    numeroAtaque = float('-inf')
    nome = None

    while fila:
        vertice_atual, ataque_atual = fila.popleft()
        visitados.add(vertice_atual)

        # Verificar o atributo 'ataque' do nó atual
        if ataque_atual > numeroAtaque:
            numeroAtaque = ataque_atual
            nome = vertice_atual

        for vizinho in grafo.neighbors(vertice_atual):
            if vizinho not in visitados:
                fila.append((vizinho, grafo.nodes[vizinho]['total']))

    return nome, numeroAtaque

def infos():
    Full_lista = listaHebron + listaTulkarm + listaAlQuds + listaJericho + listaJenin + listaSalfit + listaNablus + listaBethlehem + listaTubas + listaQalqiliya + listaRamallah
    case = int(input("Digite o case: "))

    if(case == 1):
        grafo(listaHebron,"Hebron")
    elif(case == 2):
        grafo(listaTulkarm,"Tulkarm")
    elif(case == 3):
        grafo(listaAlQuds,"Hizma")
    elif(case == 4):
        grafo(listaJericho,"Jericho")
    elif(case == 5):
        grafo(listaJenin,"Jenin R.C.")
    elif(case == 6):
        grafo(listaSalfit,"Haris")
    elif(case == 7):
        grafo(listaNablus,"Duma")
    elif(case == 8):
        grafo(listaBethlehem,"Nahhalin")
    elif(case == 9):
        grafo(listaTubas,"Bardalah")
    elif(case == 10):
        #sem regiao
        grafo(listaQalqiliya,"")
    elif(case == 11):
        grafo(listaRamallah,"al-Mughayir")
    elif(case == 12):
        grafo(Full_lista,"Hebron")


    #salvarCSV3(Full_lista)        
    