
Vue.component('button-counter', {
   template: '#button-counter-template',
   data: function () {
       return {
           count: 0
       }
   }
})

new Vue({ el: '#app' })

new Vue({
   el: '#app',
   methods: {
       incrementCount: function() {
           // Call Flask API
           fetch('/api/increment', { method: 'POST' })
               .then(response => response.json())
               .then(data => {
                   console.log(data.message);
                   this.count++;
               })
       }
   }
})
