import streamlit as st
import feedparser

st.write('''
    # Das StonedLack Universum 🏈
    Das Universum umfasste in der Saison 2024 über 60 Dynasty- und Redraftligen. Auf den folgenden Seiten findet ihr Einblicke zu den wöchentlichen Statistiken, Matchups, zu den Drafts etc.
    ''')

with st.expander("StonedLack News", icon=":material/news:", expanded=True):
    st.write(''' 
    #### Community-Mock-Draft am 21.04.2025 ab 21:30 Uhr
    Der NFL-Draft steht an, doch kurz vor dem Großereignis in Green Bay steht im Stoned Lack Universum der Community Mock Draft an.
    Im [Discord](https://discord.com/channels/793571503681175573/1357360178978361555/1357361110923346184) kann man sich dazu noch anmelden.
             
    Im Mock Draft werden die Zuschauer live in die Show geholt und dürfen für "ihre" Franchise den First Round Pick tätigen. 
    Gut die Hälfte der Teams stehen noch zur Wahl, also zwar noch genug Zeit, sich ein Team auszusuchen. Wer jedoch sein für Lieblingsteam picken möchte, sollte sich ranhalten.
             
    Der Community Mock Draft ist jedes Jahr ein Highlight der Offseason (wenn nicht sogar der ganzen Saison), also macht mit und pickt den nächsten Superstar für Eure NFL-Franchise!
             
    ---
    
    #### Erster Dynasty-Draft 2025 läuft
    In der neu gegründeten Stoned Lack Dynasty 32 läuft gerade der Verteran Draft. Alle Picks können hier auf der Seite unter Dynasty -> Drafts oder auf sleeper (https://sleeper.com/draft/nfl/1207100722546475008) abgerufen werden.                 
    
    ---

    #### Stoned Lack bei der American Football Madness in Düsseldorf dabei
    Wie die beiden am Montag im Podcast verrieten, wird im Rahmen der American Football Madness (AFM) in Düsseldorf am 31.05.2025 ein Live-Podcast von Stoned Lack aufgenommen. 
    Tickets und Infos zum Event gibt es unter folgendem [Link](https://www.americanfootballmadness.de/).
    
    ---
             
    #### Neue Stoned Lack Dynasty-Liga gegründet
    Die neue Fantasy Saison ist noch eine Weile hin, doch die Vorfreude ist bereits spürbar. Mit der Stoned Lack Dynasty 32 wurde nun eine weitere SL Liga gegründet. 
    Altbekannte und neue Manager werden dann ab September ihre Teams gegeneinander antreten lassen.     

    ---
      
    #### kunfc. ist der Champ of Champs 2024
    Mit dem Ausgang des Superbowls entschied sich auch die Frage, wer sich im Champ of Champs-Spiel durchsetzt. Letzlich ergattert sich kunfc. (sleeper: kunfc) den begehrten Titel und den Siegespreis.
    
    Das Champ of Champs-Spiel im Superbowl bestand aus der Auswahl von drei Spielern, deren Fantasy-Performances mit einem Faktor multipliziert wurde. Bester Fantasy Spieler der Runde war Worthy mit insgesamt 107,10 Fantasy Punkten (bei einem Faktor x3). 
    
    kunfc setzte auf Worthy, AJ Brown und Goedert und sammelte somit insgesamt 161,1 Fantasy Punkte, was die Verteidigung der Führung und den Gesamtsieg bedeutete. Glückwunsch zum Sieg und viel Spaß mit dem Preis.
  
    ---
        
    #### Aktuelle Podcast-Folgen''')
    # RSS-Feed URL
    RSS_FEED_URL = "https://www.youtube.com/feeds/videos.xml?playlist_id=PLVPzmyE6fIhQg_kqkLNoH1fd4oyv2D5X6"

    def fetch_rss_feed(url):
        return feedparser.parse(url)

    feed = fetch_rss_feed(RSS_FEED_URL)

    if feed.entries:
        for entry in feed.entries[:5]:  # Zeigt die letzten 10 Einträge an
            st.markdown(
                f''' 
                [{entry.title}]({entry.link})  
                ''')
    else:
        st.write("Keine Artikel gefunden.")

with st.expander("NFL News", icon=":material/news:", expanded=True):
    # URL des Rotowire NFL RSS-Feeds
    RSS_FEED_URL = "https://www.rotowire.com/rss/news.php?sport=NFL"

    def get_news():
        feed = feedparser.parse(RSS_FEED_URL)
        return feed.entries  # Liste der News-Artikel
    news_entries = get_news()

    for entry in news_entries:
        st.write(f"#### {entry.title}")
        st.write(f"📰 {entry.published}")
        st.text(entry.summary)
        st.markdown(f"🔗 [Zum Artikel]({entry.link})", unsafe_allow_html=True)
        st.write("---")

with st.expander("About", icon=":material/question_mark:"):
    st.write(
        '''
    Willkommen auf der Streamlit-Infoseite des StonedLack Fantasy Football Podcasts. 
        
    _**Hinweis/Disclaimer:** Die Seite wird privat betrieben und dient nur dem Zwecke der Aufbereitung von frei zugänglichen Daten aus der sleeper-API ([Link](https://docs.sleeper.com/)).
    Die Seite steht in keiner Verbindung zu den Podcast-Autoren und wird als zusätzliches Angebot ("Fan-Page") betrieben._
    
    #### Stoned _what_ !?
    StonedLack ist ein Live-Podcast der beiden Fantasy Football-Heads **Stoni** und **Lack** aus Wien.
    Beinahe das ganze Jahr über betreiben sie den Podcast, der u. a. live auf dem [youtube-Kanal](https://www.youtube.com/@stonedlack) verfolgt werden kann.
    Der Podcast ist auch auf allen gängigen Streaming-Plattformen verfügbar.
    
    Um den Podcast hat sich mittlerweile eine große Gemeinde Fantasy Football-Begeisterter versammelt, die den Podcast verfolgt, selbst aktiv einbringt etc. pp.
    Fast aller Austausch in der Community findet auf dem Discord-Channel ([Einladungslink](https://discord.gg/V9pt9MZ6Ch)) statt.
        
    #### StonedLack Ligen
    Seit vielen Jahren organisieren StonedLack eigene Ligen, in denen die Zuschauenden und -hörenden gegeneinander antreten. 
    Jedes Jahr werden so bspw. Redraftligen organisiert, die dann live im Podcast ausgelost werden. 
        
    Des Weiteren gibt es viele Dynasty-Ligen, die über viele Jahre hinweg bespielt werden. 
        
    Die Gewinner jeder Liga spielen um die **'MaryoLarry Trophy'** und den Gesamtsieg.
        
    #### Schön und gut, aber was soll das hier?!
    Gute Frage. Ich höre den Podcast seit gut drei Jahren. 
    Um allen aus der Community einen Zugang zu den Redraftligen zu gewähren, habe ich vor 2 Jahren angefangen, die API der Plattform [sleeper](sleeper.com), 
    auf der die Ligen organisiert sind, auszulesen.
        
    Angefangen hat alles mit der Idee, ein ADP-Draftboard aus allen Ligen zu generieren, also ein Spielerranking über alle Drafts der 2023er-StonedLack Redraftligen zu erstellen.
    In der Folge habe ich begonnen, wöchentliche Updates zu allen Ligen in Discord zu schreiben. Motivation war auch, die Programmiersprache `python` besser kennen zu lernen.
        
    Nun mündet das Ganze in meinem vorerst größten und sichtbarstem Projekt, dieser Streamlit-Plattform. 
    Der Gedanke dahinter ist, für die kommende Fantasy-Saison eine Plattform zu bauen, in der man mehr Informationen bieten und darstellen kann,
    als in einer Discord-Nachricht. Daher ist die Seite auch noch ständigen Updates und Änderungen ausgesetzt.
        
    Wer Ideen und Wünsche hat, kann diese gern äußern und mir im Discord schreiben. Ihr wisst ja, wo Ihr mich finden könnt.😉
        
    Viel Spaß auf der Seite und bei Fantasy Football!
    ''')