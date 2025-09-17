import streamlit as st
import feedparser

def fetch_rss(url, limit=None):
    feed = feedparser.parse(url)
    return feed.entries[:limit] if limit else feed.entries

# st.title("Wir bauen etwas um... Bald geht's weiter!")
def app():
    st.write('''
        # Das StonedLack Universum 🏈
        Das Universum umfasst in der Saison 2025 über 90 Dynasty- und Redraftligen. Auf den folgenden Seiten findet ihr Einblicke zu den wöchentlichen Statistiken, Matchups, zu den Drafts etc.
        ''')

    with st.expander("StonedLack News", icon=":material/news:", expanded=True):
        st.write(''' 
        #### Redraftligen 2025 ausgelost und Drafts gestartet!
        Die Redraftligen für die Saison 2025 wurden im Rahmen einer Live-Auslosung im Stoned Lack Podcast vergeben.
        Mittlerweile sind alle 48 Ligen gefüllt und die Drafts sind in vollem Gange.
        Auf der Seite "Drafts" findet ihr alle Informationen zu den Drafts, inklusive Link zum jeweiligen Draft.
        Auf der Seite "ADP Draftboard" findet ihr ein gemeinsames Draftboard aller Redraftligen.
                
        ---
        
        ''')
        # YouTube Feed
        feed_url = "https://www.youtube.com/feeds/videos.xml?playlist_id=PLVPzmyE6fIhQg_kqkLNoH1fd4oyv2D5X6"

        feed = feedparser.parse(feed_url)

        st.write(f"#### {feed.feed.title}")

        for entry in feed.entries[:5]:  # Zeigt die letzten 5 Einträge an
            col1, col2 = st.columns([1,3])
            with col2:
                st.write(f"[{entry.title}]({entry.link})")
            with col1:
                st.image(entry.media_thumbnail[0]['url'], width=150)
            # st.write("---")

    with st.expander("NFL News", icon=":material/news:", expanded=True):
        # URL des Rotowire NFL RSS-Feeds
        nfl_entries = fetch_rss("https://www.rotowire.com/rss/news.php?sport=NFL", limit=10)
        for entry in nfl_entries:
            st.markdown(
                f"""
                <div class="news-card">
                    <h5>{entry.title}</h5>
                    <p>🗓 {entry.published}</p>
                    <p>{entry.summary}</p>
                    <a href="{entry.link}" target="_blank">🔗 Zum Artikel</a>
                </div>
                """,
                unsafe_allow_html=True
            )

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