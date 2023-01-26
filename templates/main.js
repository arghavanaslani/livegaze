function myFunction() {
    var x = document.getElementById("myTopnav");
    if (x.className === "topnav") {
      x.className += "responsive";
    } else {
      x.className = "topnav";
    }
  }
  
const myForm = document.querySelector('.myForm');
const ulIdInput = document.querySelector('#ulId');
const urIdInput = document.querySelector('#urId');
const drIdInput = document.querySelector('#drId');
const dlIdInput = document.querySelector('#dlId');
const stimuli = document.querySelector('#stimuli-list');

myForm.addEventListener('submit', onsubmit);

function onSubmit(e) {
  e.preventDefault();

  if(ulIdInput.value === '') {
    alert('please enter fields')
  }
  else {
    const li = document.createElement('li');
    li.appendChild(document.createTextNode(`${ulIdInput.value}`));
    stimuli.appendChild(li);
    ulIdInput.value ='';
  }
}
