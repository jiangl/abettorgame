from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    group = {}
    group['name'] = "Justin's Group"
    group['participants'] = ['justin', 'lisa', 'brendan', 'lily', 'colin', 'kait', 'ellen', 'senem', 'nick', ' dave', 'john', 'peter']
    group['admin'] = 'justin'
    group['bets'] = [{"creator": "lisa", "bet": "will the DJ play wagon wheel", "option_1": "Yes", "option_2": "No"}, {"creator": "justin", "bet": "who will fall first off of the chairlift?", "option_1": "Lisa", "option_2": "Anyone else"}, {"creator": "colin", "bet": "Will we play slapcup", "option_1": "Yes", "option_2": "No"}, {"creator": "alexander the great long name don't care", "bet": "Lorem ipsum, or lipsum as it is sometimes known, is dummy text used in laying out print, graphic or web designs. The passage is attributed to an unknown typesetter in the 15th century who is thought to have scrambled parts of Cicero's De Finibus Bonorum et Malorum for use in a type specimen book.", "option_1": "Lorem ipsum text is a scrambled version of a passage in classical Latin derived from the Marcus Tullius Cicero's treatise on ethics, De Finibus Bonorum et Malorum, written in 54 BC. Lorem ipsum is a garbled version of that original Latin text, and is nonsensical.", "option_2": "In publishing and graphic design, Lorem ipsum is a placeholder text commonly used to demonstrate the visual form of a document or a typeface without relying on meaningful content."}]
    return render(request, 'index.html', {'group': group})