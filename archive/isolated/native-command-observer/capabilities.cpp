#define VK_ENABLE_BETA_EXTENSIONS
#include <vulkan/vulkan.h>
#include <link.h>
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>
#include <set>
#include <algorithm>
static void check(bool v){if(!v){std::fputs("CAPABILITY_QUERY_FAILED\n",stderr);std::exit(2);}}
static std::string quote(const char*s){std::string o="\"";for(;*s;++s){if(*s=='"'||*s=='\\')o+='\\';o+=*s;}return o+'"';}
int main(){
 VkApplicationInfo a{VK_STRUCTURE_TYPE_APPLICATION_INFO};a.pApplicationName="native-command-capabilities";a.apiVersion=VK_API_VERSION_1_3;VkInstanceCreateInfo ci{VK_STRUCTURE_TYPE_INSTANCE_CREATE_INFO};ci.pApplicationInfo=&a;VkInstance inst;check(vkCreateInstance(&ci,nullptr,&inst)==VK_SUCCESS);
 uint32_t n=0;check(vkEnumeratePhysicalDevices(inst,&n,nullptr)==VK_SUCCESS);std::vector<VkPhysicalDevice>devs(n);check(vkEnumeratePhysicalDevices(inst,&n,devs.data())==VK_SUCCESS);VkPhysicalDevice dev=VK_NULL_HANDLE;VkPhysicalDeviceProperties props{};
 for(auto d:devs){VkPhysicalDeviceProperties v;vkGetPhysicalDeviceProperties(d,&v);if(v.vendorID==0x1002&&v.deviceID==0x7551){dev=d;props=v;break;}}check(dev!=VK_NULL_HANDLE);
 check(vkEnumerateDeviceExtensionProperties(dev,nullptr,&n,nullptr)==VK_SUCCESS);std::vector<VkExtensionProperties>ext(n);check(vkEnumerateDeviceExtensionProperties(dev,nullptr,&n,ext.data())==VK_SUCCESS);std::set<std::string>names;for(auto&e:ext)names.insert(e.extensionName);auto has=[&](const char*s){return names.count(s)>0;};
 VkPhysicalDeviceFeatures2 f{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_FEATURES_2};VkPhysicalDeviceDeviceGeneratedCommandsFeaturesEXT dg{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_DEVICE_GENERATED_COMMANDS_FEATURES_EXT};VkPhysicalDeviceShaderEnqueueFeaturesAMDX se{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_SHADER_ENQUEUE_FEATURES_AMDX};VkPhysicalDeviceBufferDeviceAddressFeatures ba{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_BUFFER_DEVICE_ADDRESS_FEATURES};VkPhysicalDeviceDescriptorBufferFeaturesEXT db{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_DESCRIPTOR_BUFFER_FEATURES_EXT};f.pNext=&ba;
 if(has(VK_EXT_DEVICE_GENERATED_COMMANDS_EXTENSION_NAME)){dg.pNext=f.pNext;f.pNext=&dg;}if(has(VK_AMDX_SHADER_ENQUEUE_EXTENSION_NAME)){se.pNext=f.pNext;f.pNext=&se;}if(has(VK_EXT_DESCRIPTOR_BUFFER_EXTENSION_NAME)){db.pNext=f.pNext;f.pNext=&db;}vkGetPhysicalDeviceFeatures2(dev,&f);
 VkPhysicalDeviceProperties2 p{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_PROPERTIES_2};VkPhysicalDeviceDriverProperties dr{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_DRIVER_PROPERTIES};VkPhysicalDeviceDeviceGeneratedCommandsPropertiesEXT dp{VK_STRUCTURE_TYPE_PHYSICAL_DEVICE_DEVICE_GENERATED_COMMANDS_PROPERTIES_EXT};p.pNext=&dr;if(has(VK_EXT_DEVICE_GENERATED_COMMANDS_EXTENSION_NAME)){dp.pNext=p.pNext;p.pNext=&dp;}vkGetPhysicalDeviceProperties2(dev,&p);
 std::vector<std::string>libs;dl_iterate_phdr([](dl_phdr_info*i,size_t,void*data){if(i->dlpi_name&&std::string(i->dlpi_name).find("libvulkan_radeon.so")!=std::string::npos)static_cast<std::vector<std::string>*>(data)->emplace_back(i->dlpi_name);return 0;},&libs);const char*expected=std::getenv("EXPECTED_RADV_LIBRARY_PATH");check(expected&&std::find(libs.begin(),libs.end(),expected)!=libs.end());
 std::printf("{\"device\":%s,\"vendor_id\":%u,\"device_id\":%u,\"api_version\":%u,\"driver\":%s,\"driver_info\":%s,\"radv_path\":%s,",quote(props.deviceName).c_str(),props.vendorID,props.deviceID,props.apiVersion,quote(dr.driverName).c_str(),quote(dr.driverInfo).c_str(),quote(expected).c_str());
 std::printf("\"extensions\":{");bool first=true;for(auto name:{"VK_EXT_device_generated_commands","VK_NV_device_generated_commands_compute","VK_AMDX_shader_enqueue","VK_EXT_descriptor_buffer","VK_KHR_buffer_device_address"}){std::printf("%s%s:%s",first?"":",",quote(name).c_str(),has(name)?"true":"false");first=false;}
 std::printf("},\"features\":{\"deviceGeneratedCommands\":%s,\"dynamicGeneratedPipelineLayout\":%s,\"shaderEnqueue\":%s,\"shaderMeshEnqueue\":%s,\"bufferDeviceAddress\":%s,\"descriptorBuffer\":%s},\"dgc_properties\":{\"compute_stage\":%s,\"compute_pipeline_binding\":%s,\"max_sequences\":%u,\"max_pipeline_count\":%u,\"max_tokens\":%u},\"compute_device_created\":false,\"gpu_commands_submitted\":0}\n",dg.deviceGeneratedCommands?"true":"false",dg.dynamicGeneratedPipelineLayout?"true":"false",se.shaderEnqueue?"true":"false",se.shaderMeshEnqueue?"true":"false",ba.bufferDeviceAddress?"true":"false",db.descriptorBuffer?"true":"false",(dp.supportedIndirectCommandsShaderStages&VK_SHADER_STAGE_COMPUTE_BIT)?"true":"false",(dp.supportedIndirectCommandsShaderStagesPipelineBinding&VK_SHADER_STAGE_COMPUTE_BIT)?"true":"false",dp.maxIndirectSequenceCount,dp.maxIndirectPipelineCount,dp.maxIndirectCommandsTokenCount);
 vkDestroyInstance(inst,nullptr);
}
