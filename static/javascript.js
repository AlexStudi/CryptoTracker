function modifier(clicked_id) {
    let value = document.getElementById(clicked_id).value;
    if (value === 'Modifier') {
        document.getElementById(clicked_id).value = 'Valider';
        document.getElementById(clicked_id).style.backgroundColor = '#1fc36c' /*vert*/
        document.getElementsByClassName(clicked_id)[0].disabled = false;
        document.getElementsByClassName(clicked_id)[1].disabled = false;
        
    } else {
        document.editForm.submit();
    }
    return false;
}

function color_number(id){
    // color the text between HTML tag
    // Arg : id of the tag
    // A numeric value is needed in the tag
    // if value >0 the text is green, if not it is red
    try {
        let id2 = document.getElementById(id);
        let attribute_value = id2.getAttribute('value');
        let test = attribute_value >0; 
        if (test===false) {
            document.getElementById(id).style.color="#FF9586";/*red color*/
        } else {
            document.getElementById(id).style.color="#1fc36c";/*green color*/
        }
    } catch {}
}


function numStr(id) {
    // replace the text between tag by a value with thousand separator
    // Arg : id of the tag
    // A numeric value is needed in the tag
    try{
        let id2 = document.getElementById(id);
        let number = id2.getAttribute('value');
        number = new Intl.NumberFormat().format(number);
        document.getElementById(id).innerHTML = number
    } catch {}
}

function get_list_unik_id(tag_name){
    // return a list of id for the defined name of tag
    try{
        let crypo_id_list = document.getElementsByName(tag_name);
        let crypto_list_unik_id=[];
        for (const element of crypo_id_list){
            crypto_list_unik_id.push(element['id']);
        }
        return crypto_list_unik_id
    } catch {}
}

for (const element of get_list_unik_id("crypto_unik_id_colored")){
    color_number(element);
    numStr(element);
}

for (const element of get_list_unik_id("crypto_unik_id")){
    numStr(element);
}




