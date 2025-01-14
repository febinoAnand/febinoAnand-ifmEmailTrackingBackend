from django.shortcuts import render
from rest_framework import viewsets,views
from .models import UnauthUser, UserDetail
from .serializers import *
from django.http import JsonResponse, HttpResponseNotFound, HttpResponseBadRequest
import json
from django.conf import settings
from datetime import datetime, timedelta
from .models import UserDetail
from .models import Setting as UserAuthSetting
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.http import HttpResponseNotFound, HttpResponseBadRequest
from django.conf import settings
import json
import uuid
import random
from rest_framework.authtoken.models import Token
from rest_framework import generics
from .serializers import ChangePasswordSerializer
from rest_framework import status
from pushnotification.models import Setting as pushNotificaitionSettings
from pushnotification.models import NotificationAuth

from django.contrib.auth.models import Group
from django.contrib.auth.models import User  

from django.db import transaction

from django.contrib.auth.hashers import check_password
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .serializers import AuthGroupSerializer

import smsgateway.integrations as SMSgateway
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login
from rest_framework.permissions import IsAuthenticated,IsAdminUser

# Create your views here.

class UnauthUserViewSet(viewsets.ModelViewSet):
    serializer_class = UnauthUserSerializer
    queryset = UnauthUser.objects.all().order_by('-pk')
    permission_classes = [IsAuthenticated]

class UserDetailViewSet(viewsets.ModelViewSet):
    serializer_class = UserDetailSerializer
    queryset = UserDetail.objects.all().order_by('-pk')
    permission_classes = [IsAuthenticated]

class SettingViewSet(viewsets.ModelViewSet):
    serializer_class = SettingSerializer
    queryset = UserAuthSetting.objects.all().order_by('-pk')
    permission_classes = [IsAuthenticated]


class UserAuthAPI(views.APIView):
    def get(self,request):
        # print(request.body)
        return HttpResponseNotFound()
    
    def post(self,request):
        # print(request.body)
        
        responseData = {}
        
        
########################### POST FLOW ##################################

        #check valid Json data in request 
        jsondata = {}
        try:
            jsondata = json.loads(request.body)
        except Exception as e:
            print (e)                       #TODO : save the exception in Log File
            return HttpResponseNotFound()
        
        
        #check app_token valid with Settings...
        if "appToken" not in jsondata:
            return HttpResponseNotFound()
        
        if jsondata["appToken"] != settings.APP_TOKEN:
            return HttpResponseNotFound()


        #Validate the Post Data....
        userAuthSerializer = UserAuthAPISerializer(data=jsondata)
        if not userAuthSerializer.is_valid():
            return HttpResponseBadRequest()


        #getting currentDate and Time
        currentDate = datetime.now().strftime("%Y-%m-%d")
        currentTime = datetime.now().strftime("%H:%M:%S")
        currentDateTime = datetime.now()
        # print (currentDate,currentTime)

########################### POST FLOW  END HERE ##################################



########################### CHECKING USER ##################################

        # Initialize app setting models
        userAuthSetting = UserAuthSetting.objects.first()

        # Filter Mobile No and get email ID
        userDetailsList = UserDetail.objects.filter(mobile_no = jsondata['mobileno'])
        userCount = len(userDetailsList)

        existingUserEmail = ""
        existingUserMob = ""
        existingUserDeviceID = ""

        #################### Existing User ##########################
        if userCount > 0:
            print ("Existing User")

            # print(userDetailsList[0].extUser.email)
            existingUserEmail = userDetailsList[0].extUser.email
            existingUserMob = userDetailsList[0].mobile_no
            existingUserDeviceID = userDetailsList[0].device_id
            
            print("Given email->",jsondata["email"])
            print("email in db->",existingUserEmail)
            print ("Checking Email address....")

            # Existing User But email was Registered Already by another mobile.... 
            if existingUserEmail != jsondata["email"]:
                print ("Given Email id already used by another mobileno")
                maskedEmail = maskEmail(existingUserEmail)
                print ("Mask email",maskedEmail)
                responseData["status"] = "INVALID"
                responseData["message"] = "Mobile Number already registered with "+maskedEmail
                return  JsonResponse(responseData)

            # Existing User But email Registered Already....

            # add or update unauth user table with 
            unAuthUser = UnauthUser.objects.filter(mobile_no = existingUserMob)
            isUnauthUserExist = unAuthUser.exists()
            
            generatedSessionID = generateUUID()
            # OTP_call_count = unAuthUser.otp_called

            print("IsUnauthUserExist->",isUnauthUserExist)
            
            if not isUnauthUserExist:    
                print("creating new user in unauth user")
                unAuthUser = UnauthUser(
                    mobile_no = existingUserMob,
                    emailaddress = existingUserEmail,
                    createdatetime = datetime.now(),
                    device_id = jsondata["deviceID"],
                    otp_called = 0,
                    is_existing_user = True,
                    session_id = generatedSessionID
                )            
                
            else:
                print("updating user in unauth user")
                unAuthUser = unAuthUser[0]
                unAuthUser.emailaddress = jsondata["email"]
                unAuthUser.device_id = jsondata["deviceID"]
                unAuthUser.save()

            OTP_call_count = unAuthUser.otp_called
            
            OTP_call_count += 1

            if OTP_call_count > userAuthSetting.OTP_call_count:

                secondsBetweenTime = compareAndGetSeconds(unAuthUser.createdatetime,currentDateTime)
                print("seconds->",secondsBetweenTime)
                print("settings seconds ->",userAuthSetting.unAuth_user_expiry_time)
                if not secondsBetweenTime > userAuthSetting.unAuth_user_expiry_time:
                    responseData["status"] = "INVALID"
                    responseData["message"] = "Tried Too many times. Try after {minutes}min".format(minutes=int(userAuthSetting.unAuth_user_expiry_time/60))
                    return JsonResponse(responseData)
                else:
                    OTP_call_count = 0
                    OTP_call_count += 1
                

            unAuthUser.createdatetime = currentDateTime
            unAuthUser.session_id = generatedSessionID
            unAuthUser.otp_called = OTP_call_count
            unAuthUser.save()

            # existingUserDeviceID = jsondata["deviceID"]
            if existingUserDeviceID != jsondata["deviceID"]:
                responseData["status"] = "PROMPT"
                responseData["message"] = "Already this user was registered. Do you want re-register?"
                responseData["session_id"] = generatedSessionID
                return JsonResponse(responseData)

            
            generatedOTP = generate_otp()    
            
            unAuthUser.otp = generatedOTP
            unAuthUser.save()

            # call SMS Model to send
            SendOTPSMS(jsondata["mobileno"],generatedOTP)
            
            responseData["status"] = "OK"
            responseData["session_id"] = generatedSessionID
            responseData["otp_resend_interval"] = userAuthSetting.OTP_resend_interval
            responseData["otp_expiry_time"] = userAuthSetting.OTP_valid_time
            responseData["is_existing_user"] = unAuthUser.is_existing_user

            return JsonResponse(responseData)




        #################### New User ###############################
        else:
            print ("new User")
            userDetailsList = UserDetail.objects.filter(extUser__email = jsondata['email'])
            userByUserCount = len(userDetailsList)
        
            #Email id exist for another user
            if userByUserCount > 0:
                print("Error:Email id Exist for the mobile")
                #mask mobile no
                maskedMobile = maskPhoneNumber(userDetailsList[0].mobile_no)
                
                responseData["status"] = "INVALID"
                responseData["message"] = "Email Id already registered with "+maskedMobile
                return  JsonResponse(responseData)

            #Check user has pending session...
            usersInUnauth = UnauthUser.objects.filter(mobile_no = jsondata["mobileno"])
            userCount = len(usersInUnauth)


            generatedSessionID = ""

            #New user with new Session
            if userCount == 0:

                print("New User with New Session")

                # generate seesionID
                generatedSessionID = generateUUID()
                

                # generate 5 digit OTP
                generatedOTP = generate_otp()
                

                # update in the unauthuser
                unAuthUser = UnauthUser.objects.create(
                    mobile_no = jsondata["mobileno"],
                    otp = generatedOTP,
                    emailaddress = jsondata["email"],
                    session_id = generatedSessionID,
                    device_id = jsondata["deviceID"]
                )

                # call SMS Model to send
                SendOTPSMS(jsondata["mobileno"],generatedOTP)

                # send jsonresponse OTP, session token, OTP resend, OTP expiry time, exsisting user status
                responseData["status"] = "OK"
                # responseData["OTP"] = generatedOTP
                responseData["session_id"] = generatedSessionID
                responseData["otp_resend_interval"] = userAuthSetting.OTP_resend_interval
                responseData["otp_expiry_time"] = userAuthSetting.OTP_valid_time
                responseData["is_existing_user"] = False

                return JsonResponse(responseData)
            
            #New user with already Session Created...
            else:
                print("New User with Old Session")

                unAuthUser = usersInUnauth[0]
                userOTPCalled = unAuthUser.otp_called
                OTPcallLimit = userAuthSetting.OTP_call_count

                print("OTPcallCount", OTPcallLimit)
                
                #increment OTP Call count
                userOTPCalled += 1
                
                
                #checkout OTP Call Count exceed
                if not userOTPCalled >= OTPcallLimit:
                    
                
                    #Generate OTP
                    generatedOTP = generate_otp()

                    #assigning oldSessionID
                    generatedSessionID = unAuthUser.session_id

                    #update date and Time, call count, OTP 
                    unAuthUser.createdatetime = datetime.now()
                    unAuthUser.otp_called = userOTPCalled
                    unAuthUser.otp = generatedOTP
                    unAuthUser.emailaddress = jsondata["email"]
                    unAuthUser.save()

                #user Exceed retry 
                else:
                    print("OTP Call Count Exceed")
                    unAuthUserCreatedTime = unAuthUser.createdatetime
                    calculated_time = compareAndGetSeconds(unAuthUserCreatedTime,currentDateTime)

                    print("Time in seconds->",calculated_time)
                    print("Setting Seconds->",userAuthSetting.unAuth_user_expiry_time)

                    if calculated_time < userAuthSetting.unAuth_user_expiry_time:
                        responseData["status"] = "INVALID"
                        responseData["message"] = "Tried Too many times. Try after {minute}min Or Try Different Mobile number".format(minute=int(userAuthSetting.unAuth_user_expiry_time/60))
                        return JsonResponse(responseData)
                    
                    # generate new Session ID
                    generatedSessionID = generateUUID()

                    #reset OTP call count
                    userOTPCalled = 0

                    # Generate OTP
                    generatedOTP = generate_otp()

                    #update date and Time ,call count, OTP, session ID 
                    unAuthUser.createdatetime = datetime.now()
                    unAuthUser.otp_called = userOTPCalled
                    unAuthUser.otp = generatedOTP
                    unAuthUser.session_id = generatedSessionID
                    unAuthUser.save()

                #call SMS model to Send OTP
                SendOTPSMS(jsondata["mobileno"],generatedOTP)

                #send JSON response
                responseData["status"] = "OK"
                # responseData["OTP"] = generatedOTP
                responseData["session_id"] = generatedSessionID
                responseData["otp_resend_interval"] = userAuthSetting.OTP_resend_interval
                responseData["otp_expiry_time"] = userAuthSetting.OTP_valid_time
                responseData["is_existing_user"] = False

                return JsonResponse(responseData)
                    
        
    

class UserAuthPrompt(views.APIView):
    
    def get(self,request):
        # print(request.body)
        return HttpResponseNotFound()
    
    def post(self,request):
        # print(request.body)
        
        
        ########################### POST FLOW ##################################

        #check valid Json data in request 
        jsondata = {}
        try:
            jsondata = json.loads(request.body)
        except Exception as e:
            print (e)                       #TODO : save the exception in Log File
            return HttpResponseNotFound()
        
        
        #check app_token valid with Settings...
        if "appToken" not in jsondata:
            return HttpResponseNotFound()
        
        if jsondata["appToken"] != settings.APP_TOKEN:
            return HttpResponseNotFound()


        #Validate the Post Data....
        userAuthSerializer = UserAuthPromptSerializer(data=jsondata)
        if not userAuthSerializer.is_valid():
            return HttpResponseBadRequest()


        #getting currentDate and Time
        currentDate = datetime.now().strftime("%Y-%m-%d")
        currentTime = datetime.now().strftime("%H:%M:%S")
        currentDateTime = datetime.now()
        # print (currentDate,currentTime)

        ########################### POST FLOW  END HERE ##################################

        # initialize unauth user 
        responseData = {}
        userAuthSetting = UserAuthSetting.objects.first()
        unAuthUser = UnauthUser.objects.filter(session_id = jsondata["sessionID"])

        #check session id 
        if not len(unAuthUser) > 0:
            print("Session not found")
            responseData["status"] = "INVALID"
            responseData["message"] = "Session Expired Try again"
            return  JsonResponse(responseData)
        
        unAuthUser = unAuthUser[0]
        #compare device id
        if unAuthUser.device_id != jsondata["deviceID"]:
            print("Session Found device not match")
            unAuthUser.delete()
            responseData["status"] = "INVALID"
            responseData["message"] = "Device Mismatch. Try again"
            return  JsonResponse(responseData)

        #calculate time between createat and currentdatetime
        timeDifferenceInSeconds = compareAndGetSeconds(unAuthUser.createdatetime,currentDateTime)
        if timeDifferenceInSeconds > userAuthSetting.unAuth_user_expiry_time:
            print("Session Found but expired")
            unAuthUser.delete()
            responseData["status"] = "INVALID"
            responseData["message"] = "Session Expired Try again"
            return  JsonResponse(responseData)
        
        #check OTP count 
        if unAuthUser.otp_called > userAuthSetting.OTP_call_count:
            responseData["status"] = "INVALID"
            responseData["message"] = "Tried Too many times. Try after sometime"
            return JsonResponse(responseData)

        #checkpost data need to change
        if jsondata["needtochange"] != True:
            unAuthUser.delete()
            responseData["status"] = "OK"
            responseData["message"] = "Registration cancelled"
            return  JsonResponse(responseData)

        # generate OTP
        generatedOTP = generate_otp()

        # update otp in the 
        unAuthUser.otp = generatedOTP
        unAuthUser.createdatetime = currentDateTime
        unAuthUser.save()

        # call SMS api
        SendOTPSMS(unAuthUser.mobile_no,generatedOTP)
        
        # send response
        responseData["status"] = "OK"
        responseData["session_id"] = jsondata["sessionID"]
        responseData["otp_resend_interval"] = userAuthSetting.OTP_resend_interval
        responseData["otp_expiry_time"] = userAuthSetting.OTP_valid_time
        return JsonResponse(responseData)
    

class UserVerifyView(views.APIView):
    def get(self,request):
        # print(request.body)
        return HttpResponseNotFound()
    
    def post(self,request):
        print(request.body)

        ########################### POST FLOW ##################################

        #check valid Json data in request 
        jsondata = {}
        try:
            jsondata = json.loads(request.body)
        except Exception as e:
            print (e)                       #TODO : save the exception in Log File
            return HttpResponseNotFound()
        
        
        #check app_token valid with Settings...
        if "appToken" not in jsondata:
            return HttpResponseNotFound()
        
        if jsondata["appToken"] != settings.APP_TOKEN:
            return HttpResponseNotFound()


        #Validate the Post Data....
        userAuthSerializer = UserAuthVerifySerializer(data=jsondata)
        if not userAuthSerializer.is_valid():
            return HttpResponseBadRequest()


        #getting currentDate and Time
        currentDate = datetime.now().strftime("%Y-%m-%d")
        currentTime = datetime.now().strftime("%H:%M:%S")
        currentDateTime = datetime.now()
        # print (currentDate,currentTime)

        ########################### POST FLOW  END HERE ##################################


        # initialize unauth user 
        responseData = {}
        userAuthSetting = UserAuthSetting.objects.first()
        unAuthUser = UnauthUser.objects.filter(session_id = jsondata["sessionID"])

        #check session id 
        if not len(unAuthUser) > 0:
            print("Session not found")
            responseData["status"] = "INVALID"
            responseData["message"] = "Session Expired Try again"
            return  JsonResponse(responseData)
        
        
        unAuthUser = unAuthUser[0]
        #compare device id
        if unAuthUser.device_id != jsondata["deviceID"]:
            print("Session Found device not match")
            unAuthUser.delete()
            responseData["status"] = "INVALID"
            responseData["message"] = "Device Mismatch. Try again"
            return  JsonResponse(responseData)

        #calculate time between createat and currentdatetime
        timeDifferenceInSeconds = compareAndGetSeconds(unAuthUser.createdatetime,currentDateTime)
        if timeDifferenceInSeconds > userAuthSetting.unAuth_user_expiry_time:
            print("Session Found but expired")
            unAuthUser.delete()
            responseData["status"] = "INVALID"
            responseData["message"] = "Session Expired Try again"
            return  JsonResponse(responseData)
        


        # Check OTP equals 
        OTP_Wrong_time = unAuthUser.otp_wrong_count
        if str(unAuthUser.otp) != jsondata["OTP"]:
            if OTP_Wrong_time > userAuthSetting.OTP_wrong_count:
                unAuthUser.delete()
                responseData["status"] = "INVALID"
                responseData["message"] = "OTP retry exceed. Try once again"
                return  JsonResponse(responseData)
            else:
                OTP_Wrong_time += 1
                unAuthUser.otp_wrong_count = OTP_Wrong_time
                unAuthUser.save()
                responseData["status"] = "INVALID"
                responseData["message"] = "OTP Wrong"
                return  JsonResponse(responseData)

        # Genereate verification ID
        generatedVerifiationID = generateUUID()
        unAuthUser.verification_token = generatedVerifiationID
        unAuthUser.save()

       
        try:
            setting = pushNotificaitionSettings.objects.first()
            if not setting:
                responseData["status"] = "INVALID"
                responseData["message"] = "No settings found in Push Notification"
                return  JsonResponse(responseData)
                # return Response({'error': 'No settings found'}, status=status.HTTP_404_NOT_FOUND)

            responseData = {
                "status": "OK",
                "session_id": request.data.get("sessionID"),
                "verification_id": generatedVerifiationID,  # replace this with your actual generated verification ID
                "Application_id": setting.application_id
            }

            return Response(responseData, status=status.HTTP_200_OK)
        except pushNotificaitionSettings.DoesNotExist:
            responseData["status"] = "INVALID"
            responseData["message"] = "No settings found in Push Notification"
            return  JsonResponse(responseData)
        
        

class UserRegisterView(views.APIView):
    def get(self,request):
        # print(request.body)
        return HttpResponseNotFound()
    
    def post(self,request):
        print(request.body)

        ########################### POST FLOW ##################################

        #check valid Json data in request 
        jsondata = {}
        try:
            jsondata = json.loads(request.body)
        except Exception as e:
            print (e)                       #TODO : save the exception in Log File
            return HttpResponseNotFound()
        
        
        #check app_token valid with Settings...
        if "appToken" not in jsondata:
            return HttpResponseNotFound()
        
        if jsondata["appToken"] != settings.APP_TOKEN:
            return HttpResponseNotFound()


        #Validate the Post Data....
        userAuthSerializer = UserAuthRegisterSerializer(data=jsondata)
        if not userAuthSerializer.is_valid():
            return HttpResponseBadRequest()


        #getting currentDate and Time
        currentDate = datetime.now().strftime("%Y-%m-%d")
        currentTime = datetime.now().strftime("%H:%M:%S")
        currentDateTime = datetime.now()
        # print (currentDate,currentTime)

        ########################### POST FLOW  END HERE ##################################
        
        # initialize unauth user 
        responseData = {}
        userAuthSetting = UserAuthSetting.objects.first()
        unAuthUser = UnauthUser.objects.filter(session_id = jsondata["sessionID"])
        

        #check session id 
        if not len(unAuthUser) > 0:
            print("Session not found")
            responseData["status"] = "INVALID"
            responseData["message"] = "Session Expired Try again"
            return  JsonResponse(responseData)
        
        unAuthUser = unAuthUser[0]
        userDetails = UserDetail.objects.filter(extUser__email=unAuthUser.emailaddress)
        


        #calculate time between createat and currentdatetime
        timeDifferenceInSeconds = compareAndGetSeconds(unAuthUser.createdatetime,currentDateTime)
        if timeDifferenceInSeconds > userAuthSetting.unAuth_user_expiry_time:
            print("Session Found but expired")
            unAuthUser.delete()
            responseData["status"] = "INVALID"
            responseData["message"] = "Session Expired Try again"
            return  JsonResponse(responseData)
        
        
        
        #compare device id
        if unAuthUser.device_id != jsondata["deviceID"]:
            print("Session Found device not match")
            unAuthUser.delete()
            responseData["status"] = "INVALID"
            responseData["message"] = "Device Mismatch. Try again"
            return  JsonResponse(responseData)
        
        extDeviceUser = UserDetail.objects.filter(device_id = jsondata["deviceID"])
        if len(extDeviceUser):
            extDeviceUser = extDeviceUser[0]
            extDeviceUser.extUser.delete()
            print("device already used by user")
            # unAuthUser.delete()
            # responseData["status"] = "INVALID"
            # responseData["message"] = "Device Mismatch. Try again"
            # return  JsonResponse(responseData)
        

        # Verify the verification token 
        if str(unAuthUser.verification_token) != jsondata["verificationID"]:
            print("usertable-->'"+unAuthUser.verification_token+"'")
            print("post-->'"+jsondata["verificationID"]+"'")
            unAuthUser.delete()
            responseData["status"] = "INVALID"
            responseData["session_id"] = "Not Verified Try process once again"
            return JsonResponse(responseData)
        
        # create or update user model with password
        # set inactive to the user
        # save deviceid and other details in userdetails
        if len(userDetails) > 0:
            # for user in userDetails:
            #     print(user)

            userDetails = userDetails[0]
            userDetails.mobile_no = unAuthUser.mobile_no
            userDetails.designation = jsondata["designation"]
            userDetails.device_id = jsondata["deviceID"]
            userDetails.extUser.set_password(jsondata["password"])  
            userDetails.extUser.first_name = jsondata["name"]
            userDetails.extUser.is_active = False
            # userDetails.extUser.user_name.noti_token = jsondata["notificationID"]
            # userDetails.extUser.user_name.save()
            userDetails.extUser.save()
            userDetails.save()  

            pushNotificationUser = NotificationAuth.objects.filter(user_to_auth=userDetails.extUser)
            if len(pushNotificationUser)>0:
                pushNotificationUser = pushNotificationUser[0]
                pushNotificationUser.noti_token = jsondata["notificationID"]
                pushNotificationUser.save()

        else:
            user = User.objects.create_user(
                                            username=unAuthUser.emailaddress, 
                                            email= unAuthUser.emailaddress, 
                                            password=jsondata["password"],
                                            )
            user.first_name = jsondata["name"]
            user.is_active = False
            user.save()
            
            userDetails = UserDetail.objects.create(
                extUser = user,
                designation = jsondata["designation"],
                mobile_no = unAuthUser.mobile_no,
                device_id = unAuthUser.device_id
            )

            notificationUser = NotificationAuth.objects.create(
                user_to_auth = user,
                noti_token = jsondata["notificationID"]
            )
        
        # delete unauther user
        unAuthUser.delete()

        #send response
        responseData["status"] = "OK"
        responseData["session_id"] = jsondata["sessionID"]
        responseData["message"] = "Registration Successfull"
        return JsonResponse(responseData)

    

def maskEmail(email):
    parts = email.split("@")
    if len(parts) == 2:
        username, domain = parts
        masked_username = username[0:2] + '*'*(len(username)-4) + username[-2:]
        masked_domain = "*"+domain[1] + '*'*(len(domain)-3) + domain[-1]
        masked_email = masked_username + "@" + masked_domain
        return masked_email



def maskPhoneNumber(mobileNo):
    masked_number = mobileNo[:5] + '*'*(len(mobileNo)-6) + mobileNo[-2:]
    return masked_number

def generate_otp():
    otp = ""
    for _ in range(5):
        otp += str(random.randint(0, 9))
    return otp


def SendOTPSMS(number,OTPno):
    otpmessage = "Verification Code: {OTP}".format(OTP= OTPno)
    print ("OTP Sent",otpmessage)
    SMSgateway.sendSMS(number,otpmessage)

def compareAndGetSeconds(fromDateTime,toDateTime):
    return (toDateTime - fromDateTime).total_seconds()


def generateUUID():
    return str(uuid.uuid4())

class ResendOTPView(views.APIView):
    def get(self,request):
        # print(request.body)
        return HttpResponseNotFound()
    def post(self, request):

        ########################### POST FLOW ##################################

        #check valid Json data in request 
        jsondata = {}
        try:
            jsondata = json.loads(request.body)
        except Exception as e:
            print (e)                       #TODO : save the exception in Log File
            return HttpResponseNotFound()
        
        
        #check app_token valid with Settings...
        if "appToken" not in jsondata:
            return HttpResponseNotFound()
        
        if jsondata["appToken"] != settings.APP_TOKEN:
            return HttpResponseNotFound()


        #Validate the Post Data....
        userAuthSerializer = UserAuthResendSerializer(data=jsondata)
        if not userAuthSerializer.is_valid():
            return HttpResponseBadRequest()


        #getting currentDate and Time
        currentDate = datetime.now().strftime("%Y-%m-%d")
        currentTime = datetime.now().strftime("%H:%M:%S")
        currentDateTime = datetime.now()
        # print (currentDate,currentTime)

        ########################### POST FLOW  END HERE ##################################


        unAuthUser = UnauthUser.objects.filter(session_id=jsondata["sessionID"]).first()

        # if not unauth_user:
        #     return HttpResponseNotFound("Session not found")
        #compare device id


        responseData = {}
        if not unAuthUser:
            responseData["status"] = "INVALID"
            responseData["message"] = "Session Expired Try again"
            return  JsonResponse(responseData)
        


        if unAuthUser.device_id != jsondata["deviceID"]:
            # print("Session Found device not match")
            unAuthUser.delete()
            responseData["status"] = "INVALID"
            responseData["message"] = "Device Mismatch. Try again"
            return  JsonResponse(responseData)
            
        
        user_auth_setting = UserAuthSetting.objects.first()
        # expiry_time = user_auth_setting.unAuth_user_expiry_time

        # current_time = datetime.now()
        # session_creation_time = unAuthUser.createdatetime
        # time_difference = (currentDateTime - session_creation_time).total_seconds()

        # if time_difference > expiry_time:
        #     response_data["status"] = "INVALID"
        #     response_data["message"] = "Session Expired Try again"
        #     return  JsonResponse(response_data)
        
        OTP_call_count = unAuthUser.otp_called
            
        OTP_call_count += 1

        if OTP_call_count > user_auth_setting.OTP_call_count:

            secondsBetweenTime = compareAndGetSeconds(unAuthUser.createdatetime,currentDateTime)
            print("seconds->",secondsBetweenTime)
            print("settings seconds ->",user_auth_setting.unAuth_user_expiry_time)
            if not secondsBetweenTime > user_auth_setting.unAuth_user_expiry_time:
                responseData["status"] = "INVALID"
                responseData["message"] = "Tried Too many times. Try after {minutes}min".format(minutes=int(user_auth_setting.unAuth_user_expiry_time/60))
                return JsonResponse(responseData)
            else:
                OTP_call_count = 0
                OTP_call_count += 1

        new_otp = generate_otp()
        unAuthUser.otp = new_otp
        unAuthUser.createdatetime = currentDateTime
        unAuthUser.otp_called = OTP_call_count
        unAuthUser.save()
        SendOTPSMS(unAuthUser.mobile_no, new_otp)

        response_data = {
            "status": "OK",
            "message": "OTP resent successfully",
            "session_id": jsondata["sessionID"],
            "otp_resend_interval": user_auth_setting.OTP_resend_interval,
            "otp_expiry_time": user_auth_setting.OTP_valid_time
        }
        return JsonResponse(response_data)
    





class RevokeAuthToken(APIView):
    def delete(self, request):
        token_key = request.query_params.get('token')

        if not token_key:
            return Response({'error': 'Token not provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the token exists
        try:
            token = Token.objects.get(key=token_key)
        except Token.DoesNotExist:
            return Response({'error': 'Token not found'}, status=status.HTTP_404_NOT_FOUND)

        # Delete the token
        token.delete()

        return Response({'message': 'Token revoked successfully'}, status=status.HTTP_204_NO_CONTENT)


    



class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = AuthGroupSerializer
    permission_classes = [IsAuthenticated]





                                #user_Login_view#


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        print("Received a POST request to /Userauth/userlogin/")

        # Use request.data to handle the request body
        jsondata = request.data
        print(f"Parsed JSON data: {jsondata}")

        # Check app_token validity
        if "app_token" not in jsondata or jsondata["app_token"] != settings.APP_TOKEN:
            print("Invalid or missing app_token")
            return HttpResponseNotFound()

        # Validate the POST data
        if jsondata["username"] == "demo@ifm.com" and jsondata["notification_id"] == "":
            # print ("demouser")
            jsondata.update({"notification_id":str(uuid.uuid4())})

        serializer = LoginSerializer(data=jsondata)
        if not serializer.is_valid():
            print("Invalid POST data: ", serializer.errors)
            return HttpResponseBadRequest()

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        device_id = serializer.validated_data['device_id']
        notification_id = serializer.validated_data['notification_id']

        print(f"Username: {username}, Password: {password}, Device ID: {device_id}, Notification ID: {notification_id}")

        user = User.objects.filter(username=username).first()
        print(f"User found: {user}")

        if user and not user.is_active:
            print("User account is inactive")
            return Response({'status': 'INACTIVE', 'message': 'Your Account is Inactive'}, status=status.HTTP_200_OK)

        user_detail = UserDetail.objects.filter(extUser=user).first()
        print(f"User detail found: {user_detail}")

        if user_detail and (username == 'demo@ifm.com' or device_id in user_detail.device_id):
            if user and user.check_password(password):
                token, created = Token.objects.get_or_create(user=user)
                print(f"Token created: {token.key}, Token status: {'created' if created else 'retrieved'}")

                notification_auth = NotificationAuth.objects.filter(user_to_auth=user).first()
                if notification_auth:
                    notification_auth.noti_token = notification_id
                    notification_auth.save()
                    print(f"Notification auth updated for user: {user}")
                else:
                    NotificationAuth.objects.create(user_to_auth=user, noti_token=notification_id)
                    print(f"Notification auth created for user: {user}")

                user_auth_setting = UserAuthSetting.objects.first()
                if user_auth_setting:
                    user_expiry_time = str(user_auth_setting.all_user_expiry_time)
                else:
                    user_expiry_time = "Not Set"

                return Response({
                    'status': 'OK',
                    'token': token.key,
                    'message': 'Login successful',
                    'user_expiry_time': user_expiry_time
                }, status=status.HTTP_200_OK)

            print("Invalid credentials")
            return Response({'status': 'INVALID', 'message': 'Invalid Credentials'}, status=status.HTTP_200_OK)
        else:
            print("Device mismatch or user detail not found")
            return Response({'status': 'DEVICE_MISMATCH', 'message': 'Account already used in another device. Redo Registration'}, status=status.HTTP_200_OK)


#                                    #user_Logout_view#

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
            serializer = LogoutSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            app_token = serializer.validated_data.get('app_token')
            device_id = serializer.validated_data.get('device_id')
            header_token = request.headers.get('Authorization')

            if app_token != settings.APP_TOKEN:
                return Response({'status': 'INVALID', 'message': 'Invalid app token'}, status=status.HTTP_400_BAD_REQUEST)

            if not header_token or not header_token.startswith('Token '):
                return Response({'status': 'INVALID', 'message': 'Authorization header missing or invalid'}, status=status.HTTP_400_BAD_REQUEST)

            token_key = header_token.split()[1]

            try:
                token = Token.objects.get(key=token_key)
            except Token.DoesNotExist:
                return Response({'status': 'INVALID', 'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

            user_id = token.user_id
            user_detail = UserDetail.objects.filter(extUser_id=user_id, device_id=device_id).first()

            if not user_detail:
                return Response({'status': 'INVALID', 'message': 'Invalid device ID'}, status=status.HTTP_400_BAD_REQUEST)

            token.delete()

            return Response({'status': 'OK', 'message': 'Logout successful'})
                      
                      #user_changepassword_view#

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

       
        old_password = serializer.validated_data.get('old_password')
        new_password = serializer.validated_data.get('new_password')
        header_token = request.headers.get('Authorization')

        

        if not header_token or not header_token.startswith('Token '):
            return Response({'status': 'INVALID', 'message': 'Authorization header missing or invalid'}, status=status.HTTP_400_BAD_REQUEST)

        token_key = header_token.split()[1]

        try:
            token = Token.objects.get(key=token_key)
        except Token.DoesNotExist:
            return Response({'status': 'INVALID', 'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        user_id = token.user_id


        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({"status": "INVALID", "message": "User does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        if not check_password(old_password, user.password):
            return Response({"status": "INVALID", "message": "Old password is incorrect"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"status": "OK", "message": "Password updated successfully"}, status=status.HTTP_200_OK)

    def get_user_id_from_token(self, token):
        return token.user_id
    
                                 #deleteuserview

class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        
        try:
            user_detail = UserDetail.objects.get(extUser=user)
            user_detail.delete()
        except UserDetail.DoesNotExist:
            pass

        
        try:
            unauth_user = UnauthUser.objects.get(emailaddress=user.email)
            unauth_user.delete()
        except UnauthUser.DoesNotExist:
            pass

       
        user.delete()

        return Response({"success": "User and related details deleted"}, status=status.HTTP_200_OK)
    
    
    
class WebLoginView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = WebLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(request, username=username, password=password)
            if user is not None:
                token, created = Token.objects.get_or_create(user=user)
                if not request.user.is_authenticated:
                    login(request, user)
                return Response({'status': 'OK', 'message': 'Login successful', 'token': token.key})
            return Response({'status': 'INVALID', 'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class WebLogoutView(APIView):
    def post(self, request, *args, **kwargs):
        serializer =WebLogoutSerializer(data=request.data)
        if serializer.is_valid():
            token_key = serializer.validated_data['token']
            try:
                token = Token.objects.get(key=token_key)
                token.delete()
                return Response({'status': 'OK', 'message': 'Logout successful'})
            except Token.DoesNotExist:
                return Response({'status': 'INVALID', 'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AdminChangePasswordView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = AdminChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

    
        user_id = serializer.validated_data.get('user_id')
        username = serializer.validated_data.get('username')
       
        new_password = serializer.validated_data.get('new_password')
        header_token = request.headers.get('Authorization')
        


        if not header_token or not header_token.startswith('Token '):
            return Response({'status': 'INVALID', 'message': 'Authorization header missing or invalid'}, status=status.HTTP_400_BAD_REQUEST)

        token_key = header_token.split()[1]




        try:
            token = Token.objects.get(key=token_key)
        except Token.DoesNotExist:
            return Response({'status': 'INVALID', 'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

        user_id_from_token = token.user_id
        
        if not request.user.is_superuser:
            return Response({'status': 'UNAUTHORIZED', 'message': 'Only admins can change user passwords'}, status=status.HTTP_403_FORBIDDEN)

        try:
            
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'status': 'INVALID', 'message': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
       

        user.set_password(new_password)
        user.save()

        return Response({'status': 'OK', 'message': 'Password updated successfully'}, status=status.HTTP_200_OK)
    


class DemoUserActivityView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserActivitySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get('username')

        try:
            user = User.objects.get(username=username)
            is_active = user.is_active
            status_message = 'active' if is_active else 'inactive'
            return Response({'username': username, 'status': status_message}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'status': 'INVALID', 'message': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        

class DemoUpdateUserStatusView(APIView):
    # permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        serializer = UserStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get('username')
        is_active = serializer.validated_data.get('is_active')
        password = serializer.validated_data.get('password')

        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                user.is_active = is_active
                user.save()
                status_message = 'active' if is_active else 'inactive'
                return Response({'username': username, 'status': status_message}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'INVALID', 'message': 'Incorrect password'}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({'status': 'INVALID', 'message': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        


class DemoGenerateOtpView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get('username')
        mobile_no = serializer.validated_data.get('mobile_no')

        try:
            user = UnauthUser.objects.get(emailaddress=username)
        except UnauthUser.DoesNotExist:
            return Response({'status': 'INVALID', 'message': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            unauth_user = UnauthUser.objects.get(mobile_no=mobile_no)
        except UnauthUser.DoesNotExist:
            return Response({'status': 'INVALID', 'message': 'Phone number does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        if unauth_user.otp:
            otp =unauth_user.otp 
            return Response({'status': 'OK', 'message': 'OTP generated', 'otp': otp}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'INVALID', 'message': 'OTP not generated'}, status=status.HTTP_400_BAD_REQUEST)
        
class CheckTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        header_token = request.headers.get('Authorization')

        if not header_token or not header_token.startswith('Token '):
            return Response({'status': 'INVALID', 'message': 'Authorization header missing or invalid'}, status=status.HTTP_400_BAD_REQUEST)

        token_key = header_token.split()[1]

        try:
            token = Token.objects.get(key=token_key)
            return Response({'status': 'VALID', 'message': 'Token is valid'})
        except Token.DoesNotExist:
            return Response({'status': 'INVALID', 'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)