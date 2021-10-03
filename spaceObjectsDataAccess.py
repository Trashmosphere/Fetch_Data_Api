import mariadb


def retrieve_tle_entries():
    try:
        conn = mariadb.connect(
            user="root",
            password="root",
            host="34.116.176.206",
            port=3306,
            database="spaceJunk"
        )
    except mariadb.Error as e:
        return "Error connecting to the database"

    cursor = conn.cursor()

    strRes=""

    cursor.execute("SELECT LineNumber \
                    ,NoradCatID \
                    , InternationalDesignator \
                    , Epoch \
                    , Motion \
                    , MeanMotion \
                    , RadPressureCoef \
                    , IF(LineNumber = 1, 0, Element) \
                    , IF(LineNumber = 1, Element, '') \
                    FROM spaceObjectTle LIMIT 100")
    paritateLinie=0
    for entry in cursor:
        ind=0
        paritateLinie+=1
        lineSize=0
        if (paritateLinie%2==1):
            strRes+="A"
            strRes+=str(paritateLinie)
            strRes+="\n"
        for x in entry:
            if (paritateLinie%2==1):
                ind+=1
                if (ind==1):
                    strRes+=str(paritateLinie%2)
                elif(ind==2):
                    strRes+=str(x)
                    strRes+=" "
                elif(ind==3):
                    strRes+=x
                    if (len(x)==7):
                        strRes+=" "
                    else:
                        strRes+="  "
                elif(ind==4):
                    strRes+=x
                elif(ind==5):
                    if (x[0]=='-'):
                        strRes+=x
                    else:
                        strRes+=" "
                        strRes+=x
                elif(ind==6):
                    strRes+=" "
                    strRes+=x
                elif(ind==7):
                    if (x[0]=='-'):
                        strRes+=x
                    else:
                        strRes+=" "
                        strRes+=x
                elif(ind==8):
                    strRes+=x
                elif(ind==9):
                    if (len(x)==4):
                        strRes+=" "
                    strRes+=x
            else:
                ind+=1
                if (ind==1):
                    strRes+=str(2)
                    lineSize+=1
                elif(ind==2):
                    strRes+=str(x)
                    lineSize+=len(str(x))
                elif(ind==3):
                    if(len(x)==7):
                        strRes+=" "
                        lineSize+=1
                    strRes+=x
                    lineSize+=len(x)
                elif(ind==4):
                    if (len(x)==7):
                        strRes+=" "
                        lineSize+=1
                    strRes+=x
                    lineSize+=len(x)
                elif(ind==5):
                    strRes+=x
                    lineSize+=len(x)
                elif(ind==6):
                    if (len(x)==7):
                        strRes+=" "
                        lineSize+=1
                    elif(len(x)==6):
                        strRes+="  "
                        lineSize+=2
                    strRes+=x
                    lineSize+=len(x)
                elif(ind==7):
                    if (len(x)==7):
                        strRes+=" "
                        lineSize+=1
                    elif(len(x)==6):
                        strRes+="  "
                        lineSize+=2
                    strRes+=x
                    lineSize+=len(x)
                elif(ind==8):
                    if (len(x)==16):
                        strRes+=" "
                    strRes+=x
                    lineSize+=len(x)
                    while(lineSize<=61):
                        lineSize+=1
                        strRes+='5'
                    print(lineSize)
                
            strRes+=' '
            
        strRes+='\n'

    print(strRes)
    conn.close()

    return strRes
