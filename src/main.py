#encoding:utf-8

from bs4 import BeautifulSoup
import urllib.request
from tkinter import *
from tkinter import messagebox
import sqlite3
import lxml
from datetime import datetime
# lineas para evitar error SSL
import os, ssl
from numpy import integer
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context
    
    
NUM_PAGINAS = 2



# ----- VENTANA PRINCIPAL -----------------------------------------------------------------------------------------
def ventana_principal():
    raiz = Tk()
    B1 = Button(raiz, text ="Almacenar Resultados", command = cargar)
    B1.pack()
    B2 = Button(raiz, text ="Listar Jornadas", command = listarTodas)
    B2.pack()
    B3 = Button(raiz, text ="Buscar Jornadas", command = buscarJornada)
    B3.pack()
    B4 = Button(raiz, text ="Estadísticas Jornada", command = mostrarEstadisticas)
    B4.pack()
    B5 = Button(raiz, text ="Buscar Goles", command = listarGoles)
    B5.pack()
    raiz.mainloop()

        

# ----- Funciones para ALMACENAR RESULTADOS ---------------------------------------------------------------
def cargar():
    respuesta = messagebox.askyesno(title="Confirmar", message="Está usted seguro que quiere recargar los datos?")
    if respuesta:
        almacenar_bd()


def almacenar_bd():
    conn = sqlite3.connect("partidos.db")
    conn.text_factory = str
    conn.execute("DROP TABLE IF EXISTS PARTIDOS")
    conn.execute('''CREATE TABLE PARTIDOS
        (JORNADA                   INTEGER,
        EQUIPO_LOCAL               TEXT,
        EQUIPO_VISITANTE           TEXT,
        NUM_GOLES_LOCAL            INTEGER,
        NUM_GOLES_VISITANTE        INTEGER,
        GOLES_MINUTO_LOCAL         TEXT,
        GOLES_MINUTO_VISITANTE     TEXT,
        LINK                        TEXT);''')
    
    f = urllib.request.urlopen("https://resultados.as.com/resultados/futbol/primera/2023_2024/calendario/")
    s = BeautifulSoup(f, "lxml")
    lista_div_jornadas = s.find_all("div", class_="col-md-6 col-sm-6 col-xs-12")
    
    print(len(lista_div_jornadas))
    lista_link_partidos=[]
    i=1
    for div_jornada in lista_div_jornadas:
        if i<3:
            lista_div_partidos = div_jornada.find("tbody").find_all("td", class_="col-resultado finalizado")
            for partido in lista_div_partidos:
                lista_link_partidos.append((i,partido.a['href']))
        i+=1
    for (numeroJornada,linkPartido) in lista_link_partidos:
        f2= urllib.request.urlopen(linkPartido)
        s=BeautifulSoup(f2,"lxml")
        infoLocal= s.find("div",class_="scr-hdr__team is-local")
        nombreLocal= infoLocal.find("span",class_="name-large").text.strip()
        resLocal= int(infoLocal.find("span",class_="scr-hdr__score").text.strip())
        infoVisitante= s.find("div",class_="scr-hdr__team is-visitor")
        nombreVisitante= infoVisitante.find("span",class_="name-large").text.strip()
        resVisitante= int(infoVisitante.find("span",class_="scr-hdr__score").text.strip())
        golesLocal= infoLocal.find("div",class_="scr-hdr__scorers").text.strip()
        golesVisitante= infoVisitante.find("div",class_="scr-hdr__scorers").text.strip()
        print(numeroJornada,nombreLocal,nombreVisitante,resLocal,resVisitante,golesLocal,golesVisitante,linkPartido)
        conn.execute("""INSERT INTO PARTIDOS VALUES(?,?,?,?,?,?,?,?)""",(numeroJornada,nombreLocal,nombreVisitante,resLocal,resVisitante,golesLocal,golesVisitante,linkPartido))
        
    conn.commit()
    
    cursor = conn.execute("SELECT COUNT(*) FROM PARTIDOS")
    messagebox.showinfo("Base Datos",
                        "Base de datos creada correctamente \nHay " + str(cursor.fetchone()[0]) + " registros")
    conn.close()     
        


# ----- Funciones para LISTAR JORNADAS -------------------------------------------------------------------
def listarTodas():
    conn=sqlite3.connect("partidos.db")
    conn.text_factory=str
    cursor= conn.execute("SELECT * FROM PARTIDOS")
    listarJornadas(cursor)
    conn.close
def listarJornadas(cursor):
    v = Toplevel()
    v.title("JORNADAS DE LA LIGA")
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, width=150, yscrollcommand=sc.set)
    i=0
    for row in cursor:
        if row[0]!=i:
            i=row[0]
            lb.insert(END,"\n\n")
            lb.insert(END,"JORNADA "+str(i))
            lb.insert(END,"---------------------------------")
            lb.insert(END,"\n\n")
        resultado= str(row[1]+" "+str(row[3])+" - "+str(row[4])+" "+str(row[2]))
        lb.insert(END,resultado)
    lb.pack(side=LEFT, fill=BOTH)
    sc.config(command=lb.yview)

# ----- Funciones para BUSCAR JORNADAS -------------------------------------------------------------------
def buscarJornada():
    def listar(event=None):
        conn=sqlite3.connect("partidos.db")
        conn.text_factory=str
        cursor= conn.execute("SELECT * FROM PARTIDOS WHERE JORNADA LIKE '%"+str(jornada.get())+"%'")
        listarJornadas(cursor)
        conn.close
    conn= sqlite3.connect("partidos.db")
    conn.text_factory=str
    cursor=conn.execute("SELECT DISTINCT JORNADA FROM PARTIDOS")
    jornadas= []
    for i in cursor:
        jornadas.append(i)
    v=Toplevel()
    label=Label(v,text="Seleccione la jornada:")
    label.pack(side=LEFT)
    jornada=Spinbox(v,width=30,values=jornadas)
    jornada.pack(side=LEFT)
    jornada.bind("<Return>",listar)
    Button(v,text="Buscar",command=listar).pack(side=LEFT)
    conn.close()


# ----- Funciones para ESTADÍSTICAS JORNADA --------------------------------------------------------------

def mostrarEstadisticas():
    def listar(event=None):
        conn=sqlite3.connect("partidos.db")
        conn.text_factory=str
        cursor= conn.execute("SELECT * FROM PARTIDOS WHERE JORNADA LIKE '%"+str(jornada.get())+"%'")
        listarEstadisticas(cursor)
        conn.close
    conn= sqlite3.connect("partidos.db")
    conn.text_factory=str
    cursor=conn.execute("SELECT DISTINCT JORNADA FROM PARTIDOS")
    jornadas= []
    for i in cursor:
        jornadas.append(i)
    v=Toplevel()
    label=Label(v,text="Seleccione la jornada:")
    label.pack(side=LEFT)
    jornada=Spinbox(v,width=30,values=jornadas)
    jornada.pack(side=LEFT)
    jornada.bind("<Return>",listar)
    Button(v,text="Buscar",command=listar).pack(side=LEFT)
    conn.close()
def listarEstadisticas(cursor):
    numeroEmpates=0
    numeroVictoriasLocal=0
    numeroVictoriasVisitantes=0
    totalGoles=0
    v = Toplevel()
    lb = Listbox(v, width=150)
    i=0
    for row in cursor:
        i=row[0]
        if row[3]>row[4]:
            numeroVictoriasLocal+=1
            totalGoles+=row[3]
            totalGoles+=row[4]
        elif row[4]>row[3]:
            numeroVictoriasVisitantes+=1
            totalGoles+=row[3]
            totalGoles+=row[4]
        else:
            numeroEmpates+=1
            totalGoles+=row[3]
            totalGoles+=row[4]
    lb.insert(END,"JORNADA NUMERO "+str(i))
    lb.insert(END,"\n\n")
    lb.insert(END,"GOLES TOTALES: "+str(totalGoles))
    lb.insert(END,"\n\n")
    lb.insert(END,"EMPATES: "+str(numeroEmpates))
    lb.insert(END,"\n\n")
    lb.insert(END,"VICTORIAS LOCALES:"+str(numeroVictoriasLocal))
    lb.insert(END,"\n\n")
    lb.insert(END,"VICTORIAS VISITANTES: "+str(numeroVictoriasVisitantes))
    lb.insert(END,"\n\n")
    lb.pack(side=LEFT, fill=BOTH)


# ----- Funciones para BUSCAR GOLES ----------------------------------------------------------------------


def listarGoles():
    
    def et_span_no_class(tag):
        # funcion para cpmprobar si una etiqueta es span y no tiene atributo class
        return tag.name=="span" and not tag.has_attr('class')
    
    def mostrar_equipo_l():
        #actualiza la lista de los equipos que juegan como local en la jornada seleccionada
        conn = sqlite3.connect('partidos.db')
        conn.text_factory = str
        cursor= conn.execute("""SELECT EQUIPO_LOCAL FROM PARTIDOS WHERE JORNADA=? """,(int(en_j.get()),))
        en_l.config(values=[i[0] for i in cursor])
        conn.close()
        
    def mostrar_equipo_v():
        #actualiza el equipo que juega como visitante en la jornada y equipo local seleccionados
        conn = sqlite3.connect('partidos.db')
        conn.text_factory = str
        cursor = conn.execute("""SELECT EQUIPO_VISITANTE FROM PARTIDOS WHERE JORNADA=? AND EQUIPO_LOCAL LIKE ?""",(int(en_j.get()),en_l.get()))
        en_v.config(textvariable=vis.set(cursor.fetchone()[0]))
        conn.close
        
    def cambiar_jornada():
        #se invoca cuando cambia la jornada
        mostrar_equipo_l()
        mostrar_equipo_v()
            
    def listar_busqueda():
        conn = sqlite3.connect('partidos.db')
        conn.text_factory = str
        cursor = conn.execute("""SELECT LINK,EQUIPO_LOCAL,EQUIPO_VISITANTE FROM PARTIDOS WHERE JORNADA=? AND EQUIPO_LOCAL LIKE ? AND EQUIPO_VISITANTE LIKE ?""",(int(en_j.get()),en_l.get(),en_v.get()))
        partido = cursor.fetchone()
        enlace = partido[0]
        conn.close()
        f = urllib.request.urlopen(enlace)
        so = BeautifulSoup(f,"lxml")
        #buscamos los goles del equipo local
        l = so.find("div", class_="is-local").find("div", class_="scr-hdr__scorers").find_all(et_span_no_class)
        s=""
        for g in l:
            s = s + g.string.strip()
        #buscamos los goles del equipo visitante
        l = so.find("div", class_="is-visitor").find("div", class_="scr-hdr__scorers").find_all(et_span_no_class)
        s1=""
        for g in l:
            s1 = s1 + g.string.strip()
        
        goles= partido[1] + " : " + s + "\n" + partido[2] + " : " + s1
                      
        v = Toplevel()
        lb = Label(v, text=goles) 
        lb.pack()
    
    conn = sqlite3.connect('partidos.db')
    conn.text_factory = str
    #lista de jornadas para la spinbox de seleccion de jornada
    cursor= conn.execute("""SELECT DISTINCT JORNADA FROM PARTIDOS""")
    valores_j=[int(i[0]) for i in cursor]
    #lista de los equipos que juegan como local en la jornada seleccionada
    cursor= conn.execute("""SELECT EQUIPO_LOCAL FROM PARTIDOS WHERE JORNADA=?""",(int(valores_j[0]),))
    valores_l=[i[0] for i in cursor]
    conn.close()
    
    v = Toplevel()
    lb_j = Label(v, text="Seleccione jornada: ")
    lb_j.pack(side = LEFT)
    en_j = Spinbox(v,values=valores_j,command=cambiar_jornada,state="readonly")
    en_j.pack(side = LEFT)
    lb_l = Label(v, text="Seleccione equipo local: ")
    lb_l.pack(side = LEFT)
    en_l = Spinbox(v,values=valores_l,command=mostrar_equipo_v,state="readonly")
    en_l.pack(side = LEFT)
    lb_v = Label(v, text="Equipo visitante: ")
    lb_v.pack(side = LEFT)
    vis=StringVar() #variable para actualizar el equipo visitante 
    en_v = Entry(v,textvariable=vis,state=DISABLED)
    en_v.pack(side = LEFT)
    mostrar_equipo_v() #funcion para mostrar el equipo visitante en funcion de la jornada y el local
    buscar = Button(v, text="Buscar goles", command=listar_busqueda)
    buscar.pack(side=BOTTOM)

# ----- TEST --------------------------------------------------------------------------------------------
if __name__ == "__main__":
    ventana_principal()
    print("Programa finalizado!")