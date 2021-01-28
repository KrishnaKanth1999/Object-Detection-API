const image = document.getElementById('image');
const fileInput = document.getElementById('fileUploader');
const URL = "http://192.168.1.5:5000/api/"
function communicate(img_base64_url) {
imagebox = $('#imagebox')
  $.ajax({
    url: URL,
    type: "POST",
     crossDomain: true,
    contentType: "application/json",
    data: JSON.stringify({"image": img_base64_url}),
    dataType: "json"
  }).done(function(response_data) {
  console.log(response_data)
  bytestring = response_data['image']
resimage = bytestring.split('\'')[1]
imagebox.attr('src' , 'data:image/jpeg;base64,'+resimage)
  });
}

function handleFiles() {
  parseFiles(fileInput.files);
}

function parseFiles(files) {
  const file = files[0];
  const imageType = /image.*/;
  if (file.type.match(imageType)) {
    warning.innerHTML = '';
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onloadend = () => {
      image.src = reader.result;
      communicate(reader.result);
    }
  }
}

function clickUploader() {
  fileInput.click();
}



