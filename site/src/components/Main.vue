<template>
  <div class="hello">

    <b-form>
      <label class="sr-only" for="project-name">Project Name</label>
      <b-form-input
        id="project-name"
        class="mb-2 mr-sm-2 mb-sm-0"
        placeholder="myproject"
        v-model="formData.app_name"
      ></b-form-input>

      <label class="sr-only" for="environment-name">Environment Name</label>
      <b-form-input
        id="environment-name"
        class="mb-2 mr-sm-2 mb-sm-0"
        placeholder="Jane Doe"
        v-model="formData.environment"
      ></b-form-input>

      <label class="sr-only" for="region" style="margin-top: 10px;">Region</label><br>
      <b-form-select id="region" v-model="formData.region" :options="awsRegions"></b-form-select>

      <h3>Services</h3>
      <div v-for="service in formData.services" v-bind:key="service.name">

        <label class="sr-only" for="service-name">Service Name</label>
        <b-form-input
          id="service-name"
          class="mb-2 mr-sm-2 mb-sm-0"
          placeholder="myproject"
          v-model="service.service_name"
        ></b-form-input>

        <label class="sr-only" for="service-type" style="margin-top: 10px;">ServiceType</label><br>
        <b-form-select id="service-type" v-model="service.service_type" :options="serviceTypes"></b-form-select>

        <br>
        <div v-if="service.service_type === 'container'">
        <label class="sr-only" for="health-check" style="margin-top: 10px;">Health Check</label>
        <b-form-input
          id="health-check"
          class="mb-2 mr-sm-2 mb-sm-0"
          placeholder="/health"
          v-model="service.health_check"
        ></b-form-input>
        </div>

        <div v-if="service.service_type === 'container'">
        <label class="sr-only" for="inline-form-input-name">Container Port</label>
        <b-form-input
          id="inline-form-input-name"
          class="mb-2 mr-sm-2 mb-sm-0"
          placeholder="8080"
          v-model="service.container_port"
        ></b-form-input>
        <b-button variant="danger" v-on:click="deleteService(service.service_name)" style="margin-top: 5px;">delete (-)</b-button>
        </div>

      </div>
    
      <b-button variant="primary" v-on:click="addService" style="margin-top: 20px;">Add another service(+)</b-button>
    
    
      <!-- <h3>Resources</h3> -->

    </b-form>

  <hr>

  <b-button variant="primary" v-on:click="signup">
    Sign Up To Download</b-button>
  <b-button variant="success" v-on:click="generateTerraform" :disabled="terraformDisabled" style="margin-left: 5px">Download My Terraform!</b-button>


  </div>

</template>

<script>
import axios from "axios"

export default {
  name: 'Main',
  data () {
    return {
      terraformDisabled: true,
      serviceTypes: ["container", "webapp", "serverless"],
      awsRegions: {
        "us-east-1": "N. Virginia (us-east-1)",
        "us-east-2": "Ohio (us-east-2)",
        "us-west-1": "California (us-west-1)",
        "us-west-2": "Oregon (us-west-2)",
        "af-south-1": "Cape Town (af-south-1)",
        "ap-east-1": "Hong Kong (ap-east-1)",
        "ap-south-1": "Mumbai (ap-south-1)",
        "ap-northeast-3": "Osaka (ap-northeast-3)",
        "ap-northeast-2": "Seoul (ap-northeast-2)",
        "ap-northeast-1": "Tokyo (ap-northeast-1)",
        "ap-southeast-1": "Singapore (ap-southeast-1)",
        "ap-southeast-2":  "Sydney (ap-southeast-2)",
        "ca-central-1": "Canada (ca-central-1)",
        "cn-north-1": "Beijing (ca-north-1)",
        "cn-northwest-1": "Ningxia (cn-northwest-1)",
        "eu-west-1": "Ireland (eu-west-1)",
        "eu-west-2": "London (eu-west-2)",
        "eu-west-3": "Paris (eu-west-3)",
        "eu-north-1": "Stockholm (eu-north-1)",
        "eu-south-1": "Milan (eu-south-1)",
        "me-south-1": "Bahrain (me-south-1)",
        "sa-east-1": "São Paulo (sa-east-1)",
        // "us-gov-east-1": "",
        // "us-gov-west-1": "",        
      },
      formData: {
        "app_name": "myproj",
        "environment": "production",
        "region": "us-east-1",
        "services": [
          {
            "service_type": "container",
            "service_name": "my-service",
            "health_check": "/",
            "container_port": 8080,
            // "load_balancer": True,
            // "task_cpu": "256",
            // "task_memory": "1024",
            // "internal": False,
          }
        ],
        "environment_config": {
            "needs_database": false
        }
      }
    }
  },
  mounted() {
    this.terraformDisabled = localStorage.getItem("authToken") === null
  },
  methods: {
    signup() {
      const redir = `${process.env.VUE_APP_DIGGER_BACKEND}/login/github/?redirect_uri=${window.location.href}`
      console.log(redir)
      window.open(redir)
      this.terraformDisabled = false
    },
    addService() {
      this.formData.services.push({
        "service_type": "container",
        "service_name": "service" + this.formData.services.length,
        "health_check": "/",
        "container_port": 8080,        
      })
    },
    deleteService(serviceName) {
      var services = this.formData.services
      for (var i=0; i<services.length; i++) {
        if (services[i].service_name == serviceName) {
          services.splice(i, 1)
        }
      }
    },
    downloadTerraformEnabled() {
      return localStorage.getItem("authToken") !== null 
    },
    generateTerraform() {
      var formData = {...this.formData}
      formData = {
        "app_name": formData["app_name"],
        "environment": formData["environment"],
        "region": formData["region"],
        "services": {},
        "environment_config": formData["environment_config"]
      }

      formData["environment_config"]["fargate_service_exists"] = this.formData.services.filter((x) => x.service_type === "container").length > 0
      formData["environment_config"]["eks_service_exists"] = false
      formData["environment_config"]["cloudfront_service_exists"] = this.formData.services.filter((x) => x.service_type === "webapp").length > 0
      formData["environment_config"]["lambda_service_exists"] = this.formData.services.filter((x) => x.service_type === "serverless").length > 0

      // "cloudfront_service_exists": false,
      // "lambda_service_exists": false
      for (var i=0; i<formData.services.length; i++) {
        formData["services"][formData.services[i].service_name] = formData.services[i]
      }

      axios.post(process.env.VUE_APP_COOKIES_BACKEND + "/terraform", {data: formData})
        .then((res) => {
          console.log(res)
          console.log(res.data)
          console.log(res.data.url)
          window.location.href = res.data.url
        })
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
