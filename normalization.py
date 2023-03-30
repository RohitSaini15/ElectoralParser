common_mid_name=['राम',"लाल​",'दान','कुमार','कूमार','देवी','देवि','राज','राज़',"सिंह","सींह"] # remove this if it is not starting word
common_start_name=['श्री','श्रि','श्रिमति','श्रिमती','श्रीमती','श्रीमति'] #remove this if a word start from these words

# for remove matras
hindi_letters=["क","ख","ग","घ","ङ","च","छ","ज","झ","ञ","ट","ठ","ड","ढ","ण","त","थ","द","ध","न","प","फ","ब","भ","म","क़","ख़","ग़","ज़","ड़","ढ़","फ़","य","र","ल","ळ","व","ह","श","ष","स","ऱ","ऴ"]
convert_letters=["आ","ई","ऊ","ॠ","ॡ","ऐ","औ"]
converted_into=["अ","इ","उ","ऋ","ऌ","ए","ओ"]

# remove all the matras from the hindi word
def remove_matras(word):
    simple_word=""

    # convert ्र into ृ
    word=word.replace("्र","ृ")
    word=word.replace("ं","न")

    for letter in word:
        if letter in hindi_letters:
            simple_word+=letter
        elif letter in converted_into:
            simple_word+=letter
        elif letter in convert_letters:
            simple_word+=converted_into[convert_letters.index(letter)]
    
    return simple_word

def get_normalized_name(word):
    if len(word.strip()) == 0:
        return ""
    res=(word.split()[0]).strip();

    for name in common_mid_name:
        name_id=res.find(name)
        if name_id>0 and res.endswith(name):
            res=res[:name_id]
    res=remove_matras(res)
    return res;

print(get_normalized_name("मोहनलाल"))
print(get_normalized_name("मोहन राम"))