# Deploy the Application to Code Engine

**NOTE:** Before deploying, ensure you have space in the designated container registry. These steps assume images will be stored in `us.icr.io`. To determine this, go to [https://cloud.ibm.com/containers/registry/images](https://cloud.ibm.com/containers/registry/images), choose **Settings** from lefthand menu, select the region from the drop-down menu, in this case choose `Dallas`. This will show you the remaining space.  You may need to upgrade to the paid plan if planning to develop this application and save more than one image. See [Container Registry Overview](https://cloud.ibm.com/docs/Registry?topic=Registry-registry_overview) for more details.

## Using Terraform Scripts (only if code resides in public github.com repository)

To deploy using Terraform, see [Deploy the RAG LLM Application to Code Engine using Terraform](./terraform/README.md)

## Manual method

To deploy manually, see [Deploy the RAG LLM Application into Code Engine step by step](./manual-setup.md)
  
## Accessing the URL on Code Engine

Wait for the build to complete. To access the URL go into the **Applications** page within the Code Engine Project, and click the **OpenURL** link next to the newly deployed `rag-app` application

A quick sanity check with `<url>/docs` will take you to the swagger ui. To try the APIs from swagger, you will need to click the **Authorize** button at the top and add the value you set for RAG-APP-API-KEY in the environment variables

