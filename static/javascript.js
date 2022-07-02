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

function color_number(tag_name) {
    // color the text between HTML tag
    // Arg : tag name
    // A numeric value is needed in the tag
    // if value >0 the text is green, if not it is red
    let elements = document.getElementsByName(tag_name);
    try {
        for (const element of elements){
            let test = document.getElementById(element['id']).getAttribute('value') >0; 
            if (test===false) {
                document.getElementById(element['id']).style.color="#FF9586";/*red color*/
            } else {
                document.getElementById(element['id']).style.color="#1fc36c";/*green color*/
            }
        }
    } catch {}
 }

function numStr(tag_name) {
    // replace the text between tag by a value with thousand separator
    // Arg : tag name
    // A numeric value is needed in the tag
    let elements = document.getElementsByName(tag_name);
    try {
        for (const element of elements){
            format_number = new Intl.NumberFormat().format(document.getElementById(element['id']).getAttribute('value'));
            document.getElementById(element['id']).innerHTML = format_number;
        }
    } catch {}
 }

 color_number("crypto_unik_id_colored")
 numStr("crypto_unik_id_colored")
 numStr("crypto_unik_id")



