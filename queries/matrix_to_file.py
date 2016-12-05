import plotly.tools as tls
tls.set_credentials_file(username='ChristinaChung', api_key='9Qz7ub7MJHtBqdy6N6OX')
import plotly.plotly as py
import plotly.graph_objs as go

data = [
    go.Heatmap(
        z=[[0.0, 44578.222771015164, 117428.81741235932, 41251.376461884065, 76669.62876381543, 55927.32489985754, 47093.145059373564, 110151.61007297708, 26615.80599750779, 64204.18840345018], [44578.222771015164, 0.0, 44906.742156571694, 39412.95591372875, 45153.56650707716, 43005.02922370505, 42640.95518658505, 55316.54718648783, 25363.635248816012, 44300.48657086274], [117428.81741235935, 44906.74215657169, 0.0, 44151.83365983958, 91456.0931730259, 62951.1211907431, 48873.623124153404, 116848.93927688817, 30673.715622707186, 80429.73223065979], [41251.37646188406, 39412.95591372875, 44151.8336598396, 0.0, 45638.727651985384, 37371.62667055949, 35686.13439112216, 42033.88629025101, 31084.130511726435, 43519.93244313835], [76669.62876381543, 45153.56650707718, 91456.0931730259, 45638.727651985384, 0.0, 59570.57236474097, 46202.498019827624, 84867.9707134009, 28680.916932723165, 67807.93609553397], [55927.32489985754, 43005.02922370507, 62951.121190743084, 37371.62667055949, 59570.57236474097, 0.0, 44649.33037035329, 64286.7479467183, 27123.52492038373, 55872.15963062545], [47093.14505937356, 42640.955186585044, 48873.6231241534, 35686.13439112216, 46202.498019827624, 44649.33037035329, 0.0, 51889.53296058708, 26375.967328127037, 46010.47283372094], [110151.61007297707, 55316.54718648783, 116848.93927688815, 42033.88629025099, 84867.9707134009, 64286.74794671829, 51889.53296058707, 0.0, 38300.97839021663, 70968.47944480718], [26615.80599750779, 25363.635248816012, 30673.715622707186, 31084.130511726435, 28680.91693272316, 27123.52492038373, 26375.967328127037, 38300.97839021663, 0.0, 30931.830861213013], [64204.188403450185, 44300.48657086274, 80429.73223065979, 43519.93244313835, 67807.93609553397, 55872.15963062545, 46010.472833720945, 70968.47944480718, 30931.830861213017, 0.0]],
        x=['The Mayor of Casterbridge: the Life and Death of a Man of Character.',
           'Under the Greenwood Tree: A Rural Painting of the Dutch School.',
           'In sight of land',
           'Our Mutual Friend',
           'David Copperfield',
           'Can You Forgive Her?',
           'North And South',
           'Middlemarch: A Study of Provincial Life',
           'Jude the Obscure',
           'The Picture of Dorian Gray'
         ],
        y=['The Mayor of Casterbridge: the Life and Death of a Man of Character.',
           'Under the Greenwood Tree: A Rural Painting of the Dutch School.',
           'In sight of land',
           'Our Mutual Friend',
           'David Copperfield',
           'Can You Forgive Her?',
           'North And South',
           'Middlemarch: A Study of Provincial Life',
           'Jude the Obscure',
           'The Picture of Dorian Gray'
         ],
    )
]



py.iplot(data, filename='labelled-heatmap')

##
##The Mayor of Casterbridge: the Life and Death of a Man of Character.
##By Thomas Hardy
##
##Under the Greenwood Tree: A Rural Painting of the Dutch School.
##By Thomas Hardy
##
##In sight of land
##By Hardy Duffus
##
##Our Mutual Friend
##By Charles Dickens
##
##David Copperfield
##By Charles Dickens
##
##Can You Forgive Her?
##By Anthony Trollope
##
##North And South
##By Elizabeth Cleghorn Gaskell
##
##Middlemarch: A Study of Provincial Life
##By George Eliot
##
##Jude the Obscure
##By Thomas Hardy
##
##The Picture of Dorian Gray
##By Oscar Wilde
