import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { profileService } from "@/services/profile"
import { useAuthStore } from "@/store/auth"
import { errorUtils } from "@/lib/utils"
import {
  ProfileUpdateRequest,
  PasswordChangeRequest,
  ProfilePhotoResponse,
  User,
} from "@/types"

export const useProfile = () => {
  return useQuery<User>({
    queryKey: ["auth", "me"],
    queryFn: async () => profileService.getProfile(),
    retry: 1,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

export const useUpdateProfile = () => {
  const queryClient = useQueryClient()
  const { setUser } = useAuthStore()

  return useMutation<User, Error, ProfileUpdateRequest, { previousUser?: User }>({
    mutationFn: async (data) => profileService.updateProfile(data),
    onMutate: async (data) => {
      await queryClient.cancelQueries({ queryKey: ["auth", "me"] })
      const previousUser = queryClient.getQueryData<User>(["auth", "me"])

      if (previousUser) {
        const optimisticUser = {
          ...previousUser,
          ...data,
        }
        queryClient.setQueryData(["auth", "me"], optimisticUser)
        setUser(optimisticUser)
      }

      return { previousUser }
    },
    onError: (error, _variables, context) => {
      if (context?.previousUser) {
        queryClient.setQueryData(["auth", "me"], context.previousUser)
        setUser(context.previousUser)
      }
      console.error("Profile update failed:", errorUtils.getErrorMessage(error))
    },
    onSuccess: (updatedUser) => {
      setUser(updatedUser)
      queryClient.setQueryData(["auth", "me"], updatedUser)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["auth", "me"] })
    },
  })
}

export const useUploadPhoto = () => {
  const queryClient = useQueryClient()
  const { setUser } = useAuthStore()

  return useMutation<ProfilePhotoResponse, Error, File>({
    mutationFn: async (file) => profileService.uploadProfilePhoto(file),
    onSuccess: (photo) => {
      queryClient.setQueryData(["auth", "me"], (oldUser: User | undefined) => {
        if (!oldUser) return oldUser
        const updatedUser = {
          ...oldUser,
          profilePhotoUrl: photo.url,
        }
        setUser(updatedUser)
        return updatedUser
      })
    },
    onError: (error) => {
      console.error("Photo upload failed:", errorUtils.getErrorMessage(error))
    },
  })
}

export const useChangePassword = () => {
  return useMutation({
    mutationFn: async (data: PasswordChangeRequest) => profileService.changePassword(data),
    onError: (error) => {
      console.error("Change password failed:", errorUtils.getErrorMessage(error))
    },
  })
}
